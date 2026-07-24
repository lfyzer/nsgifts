"""Signed asynchronous HTTP transport for NS.Gifts API v2."""

import asyncio
import json
import random
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote, urlencode

import aiohttp
from aiohttp import ClientTimeout

from .auth import (
    HMACSigner,
    ReplayGuard,
    request_fingerprint,
    serialize_json,
)
from .config import ClientConfig
from .enums import (
    APIEndpoint,
    APIOperation,
    ContentType,
    HeaderName,
    HTTPMethod,
)
from .errors import (
    APIAuthenticationError,
    APIConnectionError,
    APIError,
    APIRequestOutcomeUnknownError,
    APITimeoutError,
    from_http_status,
)

TokenProvider = Callable[[bool, str | None], Awaitable[str]]


@dataclass(frozen=True, slots=True)
class OperationSpec:
    """Wire and retry metadata for one API operation."""

    method: HTTPMethod
    endpoint: APIEndpoint
    authenticated: bool = True
    safe_to_retry: bool = True


OPERATION_SPECS: Mapping[APIOperation, OperationSpec] = {
    APIOperation.GET_TOKEN: OperationSpec(
        HTTPMethod.POST,
        APIEndpoint.GET_TOKEN,
        authenticated=False,
    ),
    APIOperation.STOCK: OperationSpec(
        HTTPMethod.GET,
        APIEndpoint.STOCK,
    ),
    APIOperation.CREATE_ORDER: OperationSpec(
        HTTPMethod.POST,
        APIEndpoint.CREATE_ORDER,
        safe_to_retry=False,
    ),
    APIOperation.PAY_ORDER: OperationSpec(
        HTTPMethod.POST,
        APIEndpoint.PAY_ORDER,
        safe_to_retry=False,
    ),
    APIOperation.ORDER_INFO: OperationSpec(
        HTTPMethod.GET,
        APIEndpoint.ORDER_INFO,
    ),
    APIOperation.EXCHANGE_RATE: OperationSpec(
        HTTPMethod.POST,
        APIEndpoint.EXCHANGE_RATE,
    ),
    APIOperation.CHECK_BALANCE: OperationSpec(
        HTTPMethod.GET,
        APIEndpoint.CHECK_BALANCE,
    ),
    APIOperation.STEAM_GIFT_APPS: OperationSpec(
        HTTPMethod.GET,
        APIEndpoint.STEAM_GIFT_APPS,
    ),
    APIOperation.STEAM_CHECK_USER: OperationSpec(
        HTTPMethod.POST,
        APIEndpoint.STEAM_CHECK_USER,
    ),
}


class SignedTransport:
    """Serialize, sign, send, and safely retry API v2 requests."""

    def __init__(
        self,
        *,
        config: ClientConfig,
        signer: HMACSigner,
        token_provider: TokenProvider | None,
        session: Any | None = None,
        replay_guard: ReplayGuard | None = None,
        sleeper: Callable[
            [float],
            Awaitable[None],
        ] = asyncio.sleep,
        random_source: Callable[[], float] = random.random,
    ) -> None:
        """Initialize the signed transport."""
        self._config = config
        self._signer = signer
        self._token_provider = token_provider
        self._session = session
        self._owns_session = session is None
        self._replay_guard = replay_guard or ReplayGuard()
        self._sleeper = sleeper
        self._random_source = random_source
        self._session_lock = asyncio.Lock()

    async def _ensure_session(self) -> Any:
        """Return an active aiohttp session."""
        if self._session is not None and not self._session.closed:
            return self._session
        async with self._session_lock:
            if self._session is None or self._session.closed:
                self._session = aiohttp.ClientSession()
                self._owns_session = True
        return self._session

    async def close(self) -> None:
        """Close only a session created by this transport."""
        if (
            self._owns_session
            and self._session is not None
            and not self._session.closed
        ):
            await self._session.close()

    @staticmethod
    def _path_for(
        spec: OperationSpec,
        path_params: Mapping[str, Any] | None,
    ) -> str:
        """Render encoded path parameters into an endpoint template."""
        values = {
            key: quote(str(value), safe="")
            for key, value in (path_params or {}).items()
        }
        try:
            return spec.endpoint.value.format(**values)
        except KeyError as error:
            raise APIError(
                f"Missing path parameter: {error.args[0]}"
            ) from error

    @staticmethod
    def _query_string(
        query_params: Mapping[str, Any] | None,
    ) -> str:
        """Serialize query parameters once for signing and transmission."""
        if not query_params:
            return ""
        return urlencode(
            [(key, value) for key, value in query_params.items()],
            doseq=True,
        )

    @staticmethod
    async def _response_data(response: Any) -> dict[str, Any]:
        """Decode a JSON response or preserve a text error safely."""
        raw = await response.read()
        if not raw:
            return {}
        try:
            result = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return {"detail": raw.decode("utf-8", errors="replace")}
        if isinstance(result, dict):
            return result
        return {"data": result}

    @staticmethod
    def _retry_after(response: Any) -> float | None:
        """Parse a numeric Retry-After response header."""
        value = response.headers.get("Retry-After")
        if value is None:
            return None
        if not isinstance(value, str):
            return None
        try:
            return max(float(value), 0.0)
        except ValueError:
            return None

    def _retry_delay(
        self,
        retry_count: int,
        retry_after: float | None = None,
    ) -> float:
        """Return bounded exponential backoff with jitter."""
        if retry_after is not None:
            return min(retry_after, 30.0)
        base = min(2.0**retry_count, 30.0)
        return base + self._random_source() * 0.25

    @staticmethod
    def _custom_id(
        json_body: Mapping[str, Any] | None,
    ) -> str | None:
        """Extract a safe reconciliation identifier."""
        if not json_body:
            return None
        value = json_body.get("custom_id")
        return str(value) if value is not None else None

    @staticmethod
    def _is_replay_error(error: APIError) -> bool:
        """Return whether a bootstrap rejection is explicitly replay-related."""
        if type(error) is not APIAuthenticationError:
            return False
        message = error.message.lower()
        return "replay" in message or (
            "timestamp" in message
            and ("duplicate" in message or "already used" in message)
        )

    @staticmethod
    def _is_refreshable_token_error(error: APIError) -> bool:
        """Return whether a protected rejection identifies a stale token."""
        if type(error) is not APIAuthenticationError:
            return False
        message = error.message.lower()
        return "token" in message and any(
            marker in message for marker in ("expired", "invalid", "revoked")
        )

    def _sensitive_values(
        self,
        *,
        token: str | None,
        headers: Mapping[str, str],
        json_body: Mapping[str, Any] | None,
    ) -> tuple[str, ...]:
        """Collect credentials that must be removed from server errors."""
        values = [
            self._config.password.get_secret_value(),
            self._config.api_secret.get_secret_value(),
            token or "",
            headers.get(HeaderName.SIGNATURE.value, ""),
        ]
        for key in ("password", "token", "totp_code"):
            value = (json_body or {}).get(key)
            if value is not None:
                values.append(str(value))
        return tuple(value for value in values if value)

    async def _token_for(
        self,
        *,
        authenticated: bool,
        force_refresh: bool,
        rejected_token: str | None = None,
    ) -> str | None:
        """Resolve a session token for a protected operation."""
        if not authenticated:
            return None
        if self._token_provider is None:
            raise APIAuthenticationError(
                "A token provider is required for protected requests"
            )
        return await self._token_provider(force_refresh, rejected_token)

    async def _signed_headers(
        self,
        *,
        spec: OperationSpec,
        path: str,
        query: str,
        body: bytes,
        token: str | None,
    ) -> dict[str, str]:
        """Create fresh headers and a replay-safe signature."""
        fingerprint = request_fingerprint(
            spec.method,
            path,
            query,
            body,
            token,
        )
        timestamp = await self._replay_guard.timestamp_for(fingerprint)
        signature = self._signer.sign(
            spec.method,
            path,
            query,
            body,
            timestamp,
            token,
        )
        headers = {
            HeaderName.CONTENT_TYPE.value: ContentType.JSON.value,
            HeaderName.USER_AGENT.value: "nsgifts-api-python/2.0.0",
            HeaderName.USER_ID.value: str(self._config.user_id),
            HeaderName.TIMESTAMP.value: timestamp,
            HeaderName.SIGNATURE.value: signature,
        }
        if token is not None:
            headers[HeaderName.TOKEN.value] = token
        return headers

    async def request(
        self,
        operation: APIOperation,
        *,
        json_body: Mapping[str, Any] | None = None,
        path_params: Mapping[str, Any] | None = None,
        query_params: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Send a signed API operation using its exact retry policy."""
        spec = OPERATION_SPECS[operation]
        path = self._path_for(spec, path_params)
        query = self._query_string(query_params)
        body = serialize_json(json_body)
        suffix = f"?{query}" if query else ""
        url = f"{self._config.normalized_base_url}{path}{suffix}"
        token = await self._token_for(
            authenticated=spec.authenticated,
            force_refresh=False,
        )
        retry_count = 0
        refreshed_token = False
        retried_bootstrap = False

        while True:
            headers = await self._signed_headers(
                spec=spec,
                path=path,
                query=query,
                body=body,
                token=token,
            )
            session = await self._ensure_session()
            try:
                async with session.request(
                    spec.method.value,
                    url,
                    data=body,
                    headers=headers,
                    timeout=ClientTimeout(total=self._config.request_timeout),
                    allow_redirects=False,
                ) as response:
                    data = await self._response_data(response)
                    if 200 <= response.status < 300:
                        return data

                    retry_after = self._retry_after(response)
                    error = from_http_status(
                        response.status,
                        response_data=data,
                        retry_after=retry_after,
                        sensitive_values=self._sensitive_values(
                            token=token,
                            headers=headers,
                            json_body=json_body,
                        ),
                    )
                    if response.status == 401:
                        if (
                            operation is APIOperation.GET_TOKEN
                            and not retried_bootstrap
                            and self._is_replay_error(error)
                        ):
                            retried_bootstrap = True
                            continue
                        if (
                            spec.authenticated
                            and not refreshed_token
                            and self._is_refreshable_token_error(error)
                        ):
                            token = await self._token_for(
                                authenticated=True,
                                force_refresh=True,
                                rejected_token=token,
                            )
                            refreshed_token = True
                            continue

                    can_retry_status = (
                        response.status == 429 or 500 <= response.status < 600
                    )
                    if (
                        can_retry_status
                        and spec.safe_to_retry
                        and retry_count < self._config.max_retries
                    ):
                        delay = self._retry_delay(
                            retry_count,
                            retry_after,
                        )
                        retry_count += 1
                        await self._sleeper(delay)
                        continue
                    if can_retry_status and not spec.safe_to_retry:
                        raise APIRequestOutcomeUnknownError(
                            operation.value,
                            custom_id=self._custom_id(json_body),
                            cause=error,
                        ) from error
                    raise error
            except APIError:
                raise
            except (
                aiohttp.ClientError,
                asyncio.TimeoutError,
                TimeoutError,
            ) as error:
                if not spec.safe_to_retry:
                    raise APIRequestOutcomeUnknownError(
                        operation.value,
                        custom_id=self._custom_id(json_body),
                        cause=error,
                    ) from error
                if retry_count >= self._config.max_retries:
                    error_class = (
                        APITimeoutError
                        if isinstance(
                            error,
                            (asyncio.TimeoutError, TimeoutError),
                        )
                        else APIConnectionError
                    )
                    raise error_class(
                        f"{operation.value} failed after "
                        f"{retry_count + 1} attempts"
                    ) from error
                delay = self._retry_delay(retry_count)
                retry_count += 1
                await self._sleeper(delay)
