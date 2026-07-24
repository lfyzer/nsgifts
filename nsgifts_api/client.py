"""Public asynchronous client facade for NS.Gifts API v2."""

import asyncio
import logging
from typing import Any

from .auth import HMACSigner, TokenState
from .config import ClientConfig
from .enums import APIOperation
from .errors import APIAuthenticationError, APIError
from .methods import (
    AccountMethods,
    CatalogMethods,
    OrderMethods,
    SteamMethods,
)
from .models import TokenRequest, TokenResponse
from .transport import SignedTransport

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class _LibraryStreamHandler(logging.StreamHandler):
    """Marker handler that prevents duplicate library log output."""


class NSGiftsClient:
    """Secure asynchronous client for NS.Gifts API v2.

    The client lazily authenticates before the first protected request,
    refreshes the two-hour session token under a lock, and exposes
    domain-specific method groups.
    """

    def __init__(
        self,
        config: ClientConfig | None = None,
        *,
        transport: Any | None = None,
    ) -> None:
        """Initialize the client from explicit or environment settings.

        Args:
            config: Validated client settings. When omitted, settings are
                loaded from ``NSGIFTS_*`` environment variables.
            transport: Optional injected transport for tests or advanced
                integrations.
        """
        self._config = config or ClientConfig.from_env()
        self._configure_logging()
        self._token_state: TokenState | None = None
        self._auth_response: TokenResponse | None = None
        self._token_lock = asyncio.Lock()
        self._closed = False

        if transport is None:
            signer = HMACSigner(self._config.api_secret)
            self._transport = SignedTransport(
                config=self._config,
                signer=signer,
                token_provider=self._provide_token,
            )
        else:
            self._transport = transport

        self.account = AccountMethods(self._transport)
        self.catalog = CatalogMethods(self._transport)
        self.orders = OrderMethods(self._transport)
        self.steam = SteamMethods(self._transport)

    def _configure_logging(self) -> None:
        """Configure only the library logger without duplicate handlers."""
        if not self._config.enable_logging:
            return
        _logger.setLevel(self._config.log_level)
        if any(
            isinstance(handler, _LibraryStreamHandler)
            for handler in _logger.handlers
        ):
            return
        handler = _LibraryStreamHandler()
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        )
        _logger.addHandler(handler)

    def _ensure_open(self) -> None:
        """Reject reuse after client shutdown."""
        if self._closed:
            raise APIError("NSGiftsClient is closed")

    async def authenticate(
        self,
        *,
        force: bool = False,
    ) -> TokenResponse:
        """Create or refresh the short-lived session token.

        Args:
            force: Request a new token even when the current token is valid.

        Returns:
            The masked token response and its relative expiry.
        """
        self._ensure_open()
        if (
            not force
            and self._token_state is not None
            and self._auth_response is not None
            and not self._token_state.is_expiring(
                self._config.token_refresh_buffer
            )
        ):
            return self._auth_response

        async with self._token_lock:
            if (
                not force
                and self._token_state is not None
                and self._auth_response is not None
                and not self._token_state.is_expiring(
                    self._config.token_refresh_buffer
                )
            ):
                return self._auth_response

            return await self._request_token()

    async def _request_token(self) -> TokenResponse:
        """Request and store one token while the token lock is held."""
        request = TokenRequest(
            login=self._config.login,
            password=self._config.password,
        )
        data = await self._transport.request(
            APIOperation.GET_TOKEN,
            json_body=request.to_payload(),
        )
        response = TokenResponse.model_validate(data)
        if response.user_id != self._config.user_id:
            raise APIAuthenticationError(
                "Token response user_id does not match configuration"
            )
        token = response.token.get_secret_value()
        self._token_state = TokenState.issue(
            token=token,
            expires_in=response.expires_in,
        )
        self._auth_response = response
        _logger.info("Session token refreshed")
        return response

    async def _provide_token(
        self,
        force_refresh: bool,
        rejected_token: str | None = None,
    ) -> str:
        """Provide a valid token to the signed transport."""
        if not force_refresh or rejected_token is None:
            response = await self.authenticate(force=force_refresh)
            return response.token.get_secret_value()

        self._ensure_open()
        observed_state = self._token_state
        async with self._token_lock:
            if (
                self._token_state is not None
                and self._auth_response is not None
                and (
                    self._token_state is not observed_state
                    or self._token_state.value != rejected_token
                )
            ):
                return self._token_state.value
            response = await self._request_token()
        return response.token.get_secret_value()

    async def close(self) -> None:
        """Close network resources exactly once."""
        if self._closed:
            return
        self._closed = True
        self._token_state = None
        self._auth_response = None
        await self._transport.close()

    async def __aenter__(self) -> "NSGiftsClient":
        """Enter the asynchronous client context."""
        self._ensure_open()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: Any,
    ) -> None:
        """Close the client when leaving its context."""
        await self.close()
