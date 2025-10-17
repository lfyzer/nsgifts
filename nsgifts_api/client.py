import asyncio
import logging
import time
from typing import Any, Dict, Optional

import aiohttp
from aiohttp import (
    ClientConnectionError,
    ClientResponseError,
    ClientTimeout,
)

from .errors import (
    APIError,
    APIAuthenticationError,
    APIClientError,
    APIConnectionError,
    APIServerError,
    APITimeoutError,
)
from .methods import (
    IPWhitelistMethods,
    OrderMethods,
    ServicesMethods,
    SteamMethods,
    UserMethods,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
_logger = logging.getLogger(__name__)


class NSGiftsClient:
    """Client for interacting with the NS Gifts API.

    This client handles authentication, token management, and API requests to
    the NS Gifts service. It supports automatic token refresh, retry logic for
    transient errors, and server error detection with a cooldown.

    The client is organized into functional methods:
        - user: User authentication and profile operations
        - services: Service listings and categories
        - orders: Order creation and management
        - steam: Steam-specific operations
        - ip_whitelist: IP whitelist management

    Attributes:
        base_url (str): The base URL for the API.
        max_retries (int): Maximum number of retry attempts for failed requests.
        request_timeout (int): Timeout in seconds for API requests.
        server_error_cooldown (int): Cooldown in seconds after detecting a
            server error.
        token_refresh_buffer (int): Time buffer in seconds before token expiry
            to trigger refresh.
        token (Optional[str]): The current JWT token.
        token_expiry (int): Unix timestamp when the token expires.
        email (Optional[str]): User's email for authentication.
        password (Optional[str]): User's password for authentication.
        session (Optional[aiohttp.ClientSession]): The aiohttp ClientSession
            for making requests.
        user (UserMethods): User management methods.
        services (ServicesMethods): Service and category methods.
        orders (OrderMethods): Order management methods.
        steam (SteamMethods): Steam-specific methods.
        ip_whitelist (IPWhitelistMethods): IP whitelist methods.
    """

    def __init__(
        self,
        base_url: str = "https://api.ns.gifts",
        max_retries: int = 3,
        request_timeout: int = 30,
        server_error_cooldown: int = 300,
        token_refresh_buffer: int = 300,
    ):
        """Initializes the NSGiftsClient.

        Args:
            base_url (str): The base URL for the API.
            max_retries (int): Maximum retry attempts.
            request_timeout (int): Request timeout in seconds.
            server_error_cooldown (int): Cooldown after server error.
            token_refresh_buffer (int): Buffer before token expiry for refresh.
        """
        self.base_url = base_url
        self._max_retries = max_retries
        self._request_timeout = request_timeout
        self._server_error_cooldown = server_error_cooldown
        self._token_refresh_buffer = token_refresh_buffer
        self.token: Optional[str] = None
        self.token_expiry: int = 0
        self.email: Optional[str] = None
        self.password: Optional[str] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self._token_lock = asyncio.Lock()
        self._session_lock = asyncio.Lock()
        self._server_error_detected = False
        self._server_error_timestamp = 0

        # Initialize method handlers
        self.user = UserMethods(self)
        self.services = ServicesMethods(self)
        self.orders = OrderMethods(self)
        self.steam = SteamMethods(self)
        self.ip_whitelist = IPWhitelistMethods(self)

    async def __aenter__(self):
        """Enters the async context manager."""
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exits the async context manager, closing the session."""
        await self.close()

    async def close(self):
        """Closes the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None

    def _get_headers(self) -> Dict[str, str]:
        """Gets the HTTP headers for API requests.

        Returns:
            Dict[str, str]: Dictionary of headers, including Authorization
                if token is set.
        """
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def _ensure_session(self):
        """Ensures an active aiohttp session exists."""
        if not self.session or self.session.closed:
            async with self._session_lock:
                if not self.session or self.session.closed:
                    self.session = aiohttp.ClientSession(
                        raise_for_status=True,
                    )
                    _logger.debug("Created new HTTP session")

    async def _ensure_valid_token(self):
        """Ensures the token is valid, refreshing if necessary.

        Raises:
            APIAuthenticationError: If refresh fails or credentials missing.
        """
        current_time = int(time.time())
        if not self.token or (
            self.token_expiry - current_time < self._token_refresh_buffer
        ):
            async with self._token_lock:
                # Re-check inside the lock to prevent a race condition
                current_time = int(time.time())
                if not self.token or (
                    self.token_expiry - current_time
                    < self._token_refresh_buffer
                ):
                    if not self.email or not self.password:
                        raise APIAuthenticationError(
                            "Token expired, but credentials are not set "
                            "for refresh. Call login() first."
                        )
                    await self.user.login(self.email, self.password)
                    _logger.info("Token refreshed successfully")

    async def _request_with_retries(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict] = None,
        is_auth_request: bool = False,
    ) -> Dict[str, Any]:
        """Performs a request with retry and error handling logic.

        This is a centralized method to handle common request patterns.
        It handles connection errors, timeouts, and server errors with a
        backoff strategy.

        Args:
            method (str): HTTP method (e.g., 'POST').
            endpoint (str): API endpoint path.
            json_data (Optional[Dict]): Optional JSON payload.
            is_auth_request (bool): True if this is an authentication request.

        Returns:
            Dict[str, Any]: Response JSON as a dictionary.

        Raises:
            APIConnectionError: If connection fails.
            APITimeoutError: If timeout.
            APIServerError: If server error.
            APIAuthenticationError: If login fails.
            APIClientError: If client error occurs (4xx responses).
        """
        url = f"{self.base_url}{endpoint}"
        last_error = None
        await self._ensure_session()

        for attempt in range(self._max_retries):
            if (
                self._server_error_detected
                and not self._is_cooldown_expired()
                and not is_auth_request
            ):
                cooldown_remaining = (
                    self._server_error_timestamp
                    + self._server_error_cooldown
                    - int(time.time())
                )
                raise APIServerError(
                    f"API server error detected. Avoiding requests for "
                    f"{cooldown_remaining} more seconds."
                )

            try:
                async with self.session.request(
                    method,
                    url,
                    json=json_data,
                    headers=self._get_headers(),
                    timeout=self._request_timeout,
                ) as response:
                    result = await response.json()

                    # Handle token response for both login and signup
                    if (endpoint.endswith("/get_token")
                            or endpoint.endswith("/signup")):
                        if "access_token" in result:
                            self.token = result["access_token"]
                            if "valid_thru" in result:
                                self.token_expiry = result["valid_thru"]
                            else:
                                # Default to 1.5 hours if no expiry provided
                                self.token_expiry = int(time.time()) + 5400

                    return result

            except ClientResponseError as e:
                last_error = e
                if 400 <= e.status < 500:
                    if e.status == 401 and not is_auth_request:
                        _logger.warning(
                            "Received 401 Unauthorized. Attempting token "
                            "refresh..."
                        )
                        try:
                            await self._ensure_valid_token()
                            # Retry the request with the new token
                            continue
                        except APIAuthenticationError:
                            # Refresh failed, so the original 401 is a
                            # permanent issue
                            raise APIAuthenticationError(
                                "Authentication failed after token refresh."
                            ) from e
                    else:
                        raise APIClientError(
                            f"Client error at {url}: {e.status} {e.message}"
                        ) from e
                else:  # 500+
                    self._server_error_detected = True
                    self._server_error_timestamp = int(time.time())
                    raise APIServerError(
                        f"Server error at {url}: {e.status} {e.message}"
                    ) from e
            except (ClientConnectionError, ClientTimeout) as e:
                last_error = e
                error_type = (
                    "Connection error"
                    if isinstance(e, ClientConnectionError)
                    else "Request timeout"
                )
                _logger.warning(
                    f"{error_type} on attempt {attempt + 1}/"
                    f"{self._max_retries} for {url}: {e}"
                )

                if attempt < self._max_retries - 1:
                    wait_time = 1 * (2**attempt)
                    await asyncio.sleep(wait_time)
                else:
                    ErrorClass = (
                        APIConnectionError
                        if isinstance(e, ClientConnectionError)
                        else APITimeoutError
                    )
                    raise ErrorClass(
                        f"{error_type} after {self._max_retries} attempts."
                    ) from last_error

        raise APIError("Request failed after all retries.") from last_error

    def _is_cooldown_expired(self) -> bool:
        """Checks if the server error cooldown has expired."""
        current_time = int(time.time())
        return (
            self._server_error_timestamp + self._server_error_cooldown
        ) <= current_time

    def is_server_error_detected(self) -> bool:
        """Checks if a server error is currently detected.

        Returns:
            True if server error detected and cooldown active, else False.
        """
        if self._server_error_detected and self._is_cooldown_expired():
            self._server_error_detected = False
        return self._server_error_detected

    def reset_server_error_state(self) -> None:
        """Resets the server error detection state."""
        self._server_error_detected = False
        self._server_error_timestamp = 0
        _logger.info("Server error state has been manually reset")

    async def _make_authenticated_request(
        self, method: str, endpoint: str, json_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Makes an authenticated request, ensuring a valid token exists.

        Args:
            method (str): HTTP method (e.g., 'POST').
            endpoint (str): API endpoint path.
            json_data (Optional[Dict]): Optional JSON payload.

        Returns:
            Response JSON as a dictionary.

        Raises:
            APIAuthenticationError: If not authenticated or login failed.
            APIError: For other client or server errors.
        """
        if not self.token and not (self.email and self.password):
            raise APIAuthenticationError(
                "Authentication required. Call login() or signup() first."
            )
        await self._ensure_valid_token()
        return await self._request_with_retries(method, endpoint, json_data)