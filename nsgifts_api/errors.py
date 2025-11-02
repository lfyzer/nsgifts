"""API error classes for exception handling."""

from typing import Any, Dict, Optional, Union


class APIError(Exception):
    """Base exception for API client errors.
    
    This serves as the base class for all exceptions that may occur
    when interacting with the API. All specific API error types
    inherit from this class.
    
    Attributes:
        message: Error message.
        details: Additional error details.
    """
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self):
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class APIConnectionError(APIError):
    """Raised for network connection errors.
    
    This exception occurs when there are issues with the network
    connection, such as inability to establish connection to server,
    connection interruptions, DNS resolution problems, socket errors,
    or proxy connection failures.
    
    This typically indicates issues with the client's network,
    internet service provider, or intermediate network infrastructure.
    """


class APITimeoutError(APIError):
    """Raised when an API request times out.
    
    This exception occurs when an API request does not receive a
    response within the established timeout period. Timeouts may
    happen due to high network latency, server overload, long-running
    operations on server side, or network congestion.
    
    Increasing the client's timeout settings might help in some cases.
    """


class APIAuthenticationError(APIError):
    """Raised for authentication or token refresh errors.
    
    This exception occurs when there are problems with authentication,
    such as invalid credentials, expired access token, failed token
    refresh attempts, access denied to requested resource, revoked or
    invalid API keys, or account restrictions and suspensions.
    
    This typically requires user intervention to provide correct
    credentials or resolve account-related issues.
    """


class APIValidationError(APIError):
    """Raised when request data validation fails.
    
    This exception occurs when request parameters are invalid or
    missing, data format is incorrect, values are out of acceptable
    ranges, or required fields are missing.
    
    Attributes:
        field_errors: Field-specific validation errors.
    """
    
    def __init__(
        self,
        message: str,
        field_errors: Optional[Dict[str, str]] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)
        self.field_errors = field_errors or {}
    
    def __str__(self):
        base = super().__str__()
        if self.field_errors:
            errors_str = ", ".join(
                f"{k}: {v}" for k, v in self.field_errors.items()
            )
            return f"{base} | Field errors: {errors_str}"
        return base


class APIRateLimitError(APIError):
    """Raised when rate limit is exceeded.
    
    This exception occurs when too many requests sent in given time
    period, API quota exceeded, or specific endpoint rate limit
    reached.
    
    Attributes:
        retry_after: Seconds to wait before retry.
        limit: Rate limit threshold.
    """
    
    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        limit: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)
        self.retry_after = retry_after
        self.limit = limit
    
    def __str__(self):
        base = super().__str__()
        if self.retry_after:
            return f"{base} | Retry after {self.retry_after}s"
        return base


class APINotFoundError(APIError):
    """Raised when requested resource is not found.
    
    This exception occurs when Order ID does not exist, Service ID is
    invalid, User resource not found, or endpoint does not exist.
    
    Attributes:
        resource_type: Type of resource not found.
        resource_id: ID of resource not found.
    """
    
    def __init__(
        self,
        message: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)
        self.resource_type = resource_type
        self.resource_id = resource_id
    
    def __str__(self):
        base = super().__str__()
        if self.resource_type and self.resource_id:
            return (f"{base} | Resource: {self.resource_type} "
                    f"(ID: {self.resource_id})")
        return base


class APIInsufficientFundsError(APIError):
    """Raised when account balance is insufficient.
    
    This exception occurs when balance is too low to complete order
    or payment amount exceeds available funds.
    
    Attributes:
        required_amount: Amount required.
        current_balance: Current balance.
        currency: Currency code.
    """
    
    def __init__(
        self,
        message: str,
        required_amount: Optional[float] = None,
        current_balance: Optional[float] = None,
        currency: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)
        self.required_amount = required_amount
        self.current_balance = current_balance
        self.currency = currency or "RUB"
    
    def __str__(self):
        base = super().__str__()
        if self.required_amount and self.current_balance:
            return (f"{base} | Required: {self.required_amount} "
                    f"{self.currency}, Balance: {self.current_balance} "
                    f"{self.currency}")
        return base


class APIServerError(APIError):
    """Raised when the API returns a 5xx error.
    
    This exception occurs when there are problems on the server side
    (status codes 500-599), such as:
    - 500 Internal Server Error: Unexpected condition on the server
    - 502 Bad Gateway: Invalid response from an upstream server
    - 503 Service Unavailable: Server temporarily unavailable
      (maintenance or overload)
    - 504 Gateway Timeout: Upstream server failed to respond in time
    - 507 Insufficient Storage: Server storage limit reached
    
    These errors are generally temporary and not caused by the client
    request. Implementing retry logic with exponential backoff is
    recommended for handling these errors.
    
    Attributes:
        status_code: HTTP status code.
        response_data: Response data from server.
    """
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[dict] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)
        self.status_code = status_code
        self.response_data = response_data or {}

    def __str__(self):
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class APIClientError(APIError):
    """Raised when the API returns a 4xx error.
    
    This exception occurs when there are errors related to the client
    request (status codes 400-499), such as:
    - 400 Bad Request: The request was malformed or contained invalid
      parameters
    - 403 Forbidden: The client lacks necessary permissions for the
      requested resource
    - 404 Not Found: The requested resource does not exist
    - 409 Conflict: The request conflicts with the current state of
      the server
    - 422 Unprocessable Entity: The server understands the content type
      but cannot process the request
    - 429 Too Many Requests: The client has sent too many requests in
      a given time period
    
    These errors typically require modifying the request parameters or
    addressing permission issues before retrying the request.
    
    Attributes:
        status_code: HTTP status code.
        response_data: Response data from server.
    """
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[dict] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)
        self.status_code = status_code
        self.response_data = response_data or {}

    def __str__(self):
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


def from_http_status(
    status_code: int,
    message: Optional[str] = None,
    response_data: Optional[dict] = None
) -> Union[
    APIClientError,
    APIServerError,
    APINotFoundError,
    APIValidationError,
    APIRateLimitError,
    APIInsufficientFundsError,
    APIError
]:
    """Create appropriate error instance from HTTP status code.
    
    Factory function that returns specific error types based on the
    HTTP status code. For client errors (4xx), returns specific error
    subclasses like APIValidationError, APINotFoundError, etc.
    For server errors (5xx), returns APIServerError.
    
    Args:
        status_code: HTTP status code.
        message: Custom error message. If None, default message is used.
        response_data: Response data from server.
        
    Returns:
        Appropriate error instance based on status code.
    """
    if 400 <= status_code < 500:
        # Handle specific client error cases
        if status_code == 404:
            return APINotFoundError(
                message or "Resource not found",
                details={
                    "status_code": status_code,
                    "response": response_data
                }
            )
        elif status_code == 422:
            field_errors = {}
            if response_data and "detail" in response_data:
                if isinstance(response_data["detail"], list):
                    for error in response_data["detail"]:
                        if isinstance(error, dict):
                            loc = error.get("loc", ["unknown"])
                            msg = error.get("msg", "Validation error")
                            field_name = ".".join(str(x) for x in loc)
                            field_errors[field_name] = msg
            return APIValidationError(
                message or "Validation error",
                field_errors=field_errors,
                details={
                    "status_code": status_code,
                    "response": response_data
                }
            )
        elif status_code == 429:
            retry_after = None
            if response_data:
                retry_after = response_data.get("retry_after")
            return APIRateLimitError(
                message or "Rate limit exceeded",
                retry_after=retry_after,
                details={
                    "status_code": status_code,
                    "response": response_data
                }
            )
        elif status_code == 402:
            # Payment Required - insufficient funds
            required = None
            balance = None
            currency = "RUB"
            if response_data:
                required = response_data.get("required_amount")
                balance = response_data.get("current_balance")
                currency = response_data.get("currency", "RUB")
            return APIInsufficientFundsError(
                message or "Insufficient funds",
                required_amount=required,
                current_balance=balance,
                currency=currency,
                details={
                    "status_code": status_code,
                    "response": response_data
                }
            )
        
        # Default client error
        if not message:
            status_messages = {
                400: "Bad Request - Invalid parameters",
                401: "Unauthorized - Authentication required",
                403: "Forbidden - Insufficient permissions",
                409: "Conflict - Request conflicts with current state",
            }
            message = status_messages.get(
                status_code,
                f"Client error {status_code}"
            )
        
        return APIClientError(message, status_code, response_data)
    
    elif 500 <= status_code < 600:
        # Server errors
        if not message:
            status_messages = {
                500: "Internal Server Error - Unexpected condition",
                502: "Bad Gateway - Invalid upstream response",
                503: "Service Unavailable - Temporarily unavailable",
                504: "Gateway Timeout - Upstream server timeout",
                507: "Insufficient Storage - Storage limit reached",
            }
            message = status_messages.get(
                status_code,
                f"Server error {status_code}"
            )
        
        return APIServerError(message, status_code, response_data)
    
    # Fallback for unexpected status codes
    return APIError(
        message or f"Unexpected HTTP status code: {status_code}",
        details={"status_code": status_code, "response": response_data}
    )