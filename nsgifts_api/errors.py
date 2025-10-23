"""API error classes for exception handling."""


class APIError(Exception):
    ...


class APIConnectionError(APIError):
    ...


class APITimeoutError(APIError):
    ...


class APIAuthenticationError(APIError):
    ...


class APIServerError(APIError):
    def __init__(
            self,
            message: str,
            status_code: int = None,
            response_data: dict = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data or {}

    def __str__(self):
        if self.status_code:
            return f"{self.status_code}: {super().__str__()}"
        return super().__str__()

    @classmethod
    def from_status_code(
            cls,
            status_code: int,
            message: str = None,
            response_data: dict = None
    ):
        if not message:
            status_messages = {
                500: "Internal Server Error - Unexpected server condition",
                502: "Bad Gateway - Invalid response from upstream server",
                503: "Service Unavailable - Server temporarily unavailable",
                504: "Gateway Timeout - Upstream server timeout",
                507: "Insufficient Storage - Server storage limit reached",
            }

            message = status_messages.get(status_code, f"Server error {status_code}")

        return cls(message, status_code, response_data)


class APIClientError(APIError):
    def __init__(
            self,
            message: str,
            status_code: int = None,
            response_data: dict = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data or {}

    def __str__(self):
        if self.status_code:
            return f"{self.status_code}: {super().__str__()}"
        return super().__str__()

    @classmethod
    def from_status_code(
            cls,
            status_code: int,
            message: str = None,
            response_data: dict = None
    ):
        if not message:
            status_messages = {
                400: "Bad Request - Invalid parameters",
                401: "Unauthorized - Authentication required",
                403: "Forbidden - Insufficient permissions",
                404: "Not Found - Resource does not exist",
                409: "Conflict - Request conflicts with current state",
                422: "Unprocessable Entity - Invalid request format",
                429: "Too Many Requests - Rate limit exceeded",
            }

            message = status_messages.get(status_code, f"Client error {status_code}")

        return cls(message, status_code, response_data)
