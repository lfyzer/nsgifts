import asyncio
import logging
import time
import re
from typing import Any, Dict, Optional

import aiohttp
from aiohttp import ClientConnectionError, ClientResponseError, ClientTimeout

from .enums import HTTPRequestType, LogLevel, ContentType, AuthHeader, ErrorType
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


class NSGiftsClient:
    def __init__(
        self,
        base_url: str = "https://api.ns.gifts",
        max_retries: int = 3,
        request_timeout: int = 30,
        log_level: LogLevel = LogLevel.INFO,
    ):
        self.base_url = base_url
        self.max_retries = max_retries
        self.request_timeout = request_timeout
        
        logging.basicConfig(
            level=getattr(logging, log_level.value),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)
        
        self.token: Optional[str] = None
        self.token_expiry: int = 0
        self.email: Optional[str] = None
        self.password: Optional[str] = None
        
        self.session: Optional[aiohttp.ClientSession] = None
        self._token_lock = asyncio.Lock()
        self._session_lock = asyncio.Lock()

        self.user = UserMethods(self)
        self.services = ServicesMethods(self)
        self.orders = OrderMethods(self)
        self.steam = SteamMethods(self)
        self.ip_whitelist = IPWhitelistMethods(self)

    @staticmethod
    def _sanitize_input(value: str, max_length: int = 1000) -> str:
        if not isinstance(value, str):
            raise ValueError("Input must be a string")
        
        sanitized = re.sub(r'[<>"\']', '', value.strip())
        
        if len(sanitized) > max_length:
            raise ValueError(f"Input too long. Maximum {max_length} characters allowed")
        
        if not sanitized:
            raise ValueError("Input cannot be empty after sanitization")
        
        return sanitized

    @staticmethod
    def _validate_email(email: str) -> str:
        email_pattern = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
        if not email_pattern.match(email):
            raise ValueError("Invalid email format")
        return email.lower().strip()

    async def __aenter__(self):
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": ContentType.JSON.value}
        if self.token:
            headers["Authorization"] = f"{AuthHeader.BEARER.value} {self.token}"
        return headers

    async def _ensure_session(self):
        if not self.session or self.session.closed:
            async with self._session_lock:
                if not self.session or self.session.closed:
                    timeout = aiohttp.ClientTimeout(total=self.request_timeout)
                    self.session = aiohttp.ClientSession(
                        raise_for_status=True,
                        timeout=timeout,
                    )
                    self.logger.debug("Created new HTTP session")

    async def _ensure_valid_token(self):
        current_time = int(time.time())
        if not self.token or (self.token_expiry - current_time < 300):
            async with self._token_lock:
                current_time = int(time.time())
                if not self.token or (self.token_expiry - current_time < 300):
                    if not self.email or not self.password:
                        raise APIAuthenticationError(
                            "Token expired, but credentials are not set for refresh. Call login() first."
                        )
                    await self.user.login(self.email, self.password)
                    self.logger.info("Token refreshed successfully")

    async def _request_with_retries(
        self,
        method: HTTPRequestType,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        is_auth_request: bool = False,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        last_error = None
        await self._ensure_session()

        for attempt in range(self.max_retries):
            try:
                async with self.session.request(
                    method,
                    url,
                    json=json_data,
                    headers=self._get_headers(),
                ) as response:
                    try:
                        result = await response.json()
                    except aiohttp.ContentTypeError as e:
                        raise APIClientError(
                            f"Invalid JSON response from {url}: {e}",
                            status_code=response.status,
                            response_data={"content_type": response.content_type}
                        ) from e

                    if endpoint.endswith("/get_token") or endpoint.endswith("/signup"):
                        if "access_token" in result:
                            self.token = result["access_token"]
                            if "valid_thru" in result:
                                self.token_expiry = result["valid_thru"]
                            else:
                                self.token_expiry = int(time.time()) + 5400

                    return result

            except ClientResponseError as e:
                last_error = e
                if 400 <= e.status < 500:
                    if e.status == 401 and not is_auth_request:
                        self.logger.warning("Received 401 Unauthorized. Attempting token refresh...")
                        try:
                            await self._ensure_valid_token()
                            continue
                        except APIAuthenticationError:
                            raise APIAuthenticationError("Authentication failed after token refresh.") from e
                    else:
                        raise APIClientError.from_status_code(
                            e.status,
                            f"Client error at {url}: {e.message}",
                            {"url": url, "message": e.message}
                        )
                else:
                    raise APIServerError.from_status_code(
                        e.status,
                        f"Server error at {url}: {e.message}",
                        {"url": url, "message": e.message}
                    )
            except (ClientConnectionError, ClientTimeout) as e:
                last_error = e
                error_type = ErrorType.CONNECTION.value if isinstance(e, ClientConnectionError) else ErrorType.TIMEOUT.value
                self.logger.warning(f"{error_type} on attempt {attempt + 1}/{self.max_retries} for {url}: {e}")

                if attempt < self.max_retries - 1:
                    wait_time = 1 * (2**attempt)
                    await asyncio.sleep(wait_time)
                else:
                    ErrorClass = APIConnectionError if isinstance(e, ClientConnectionError) else APITimeoutError
                    raise ErrorClass(f"{error_type} after {self.max_retries} attempts.") from last_error

        raise APIError("Request failed after all retries.") from last_error

    async def _make_authenticated_request(
        self, method: HTTPRequestType, endpoint: str, json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        if not self.token and not (self.email and self.password):
            raise APIAuthenticationError("Authentication required. Call login() or signup() first.")
        await self._ensure_valid_token()
        return await self._request_with_retries(method, endpoint, json_data)