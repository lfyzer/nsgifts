"""Client configuration."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ClientConfig:
    """Configuration for NSGiftsClient.
    
    This class encapsulates all configuration parameters for the API client,
    providing type safety, validation, and easy configuration management.
    
    Attributes:
        base_url: Base URL for the NS Gifts API endpoint.
        email: Email/login for authentication. If provided with password,
            the client will automatically authenticate on initialization.
        password: Password for authentication. Required if email is provided.
        auto_auth: Whether to automatically authenticate on client initialization.
            Only works if both email and password are provided. Default: True.
        max_retries: Maximum number of retry attempts for failed requests.
            Applies to transient errors like network issues or 5xx responses.
        request_timeout: Timeout in seconds for individual API requests.
            If a request takes longer, APITimeoutError will be raised.
        server_error_cooldown: Cooldown period in seconds after detecting
            a server error (5xx). During this period, non-auth requests
            will be blocked to prevent overwhelming a failing server.
        token_refresh_buffer: Time buffer in seconds before token expiry
            to trigger automatic token refresh. E.g., if set to 300 (5 min),
            the token will be refreshed when it has less than 5 minutes
            remaining until expiry.
        enable_logging: Whether to enable internal logging. If False,
            the client will not output any logs (useful for production).
        log_level: Logging level for the client logger. Only used if
            enable_logging is True. Valid values: 'DEBUG', 'INFO', 
            'WARNING', 'ERROR', 'CRITICAL'.
    """
    
    base_url: str = "https://api.ns.gifts"
    email: Optional[str] = None
    password: Optional[str] = None
    auto_auth: bool = True
    max_retries: int = 3
    request_timeout: int = 30
    server_error_cooldown: int = 300
    token_refresh_buffer: int = 300
    enable_logging: bool = False
    log_level: str = "INFO"
    
    def __post_init__(self):
        """Validate configuration parameters after initialization.
        
        Raises:
            ValueError: If any parameter is invalid.
        """
        if self.max_retries < 0:
            raise ValueError("max_retries must be >= 0")
        
        if self.request_timeout <= 0:
            raise ValueError("request_timeout must be > 0")
        
        if self.server_error_cooldown < 0:
            raise ValueError("server_error_cooldown must be >= 0")
        
        if self.token_refresh_buffer < 0:
            raise ValueError("token_refresh_buffer must be >= 0")
        
        if not self.base_url:
            raise ValueError("base_url cannot be empty")
        
        if not self.base_url.startswith(("http://", "https://")):
            raise ValueError("base_url must start with http:// or https://")
        
        valid_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
        if self.log_level.upper() not in valid_levels:
            raise ValueError(
                f"log_level must be one of {valid_levels}, "
                f"got '{self.log_level}'"
            )
        
        if self.email and not self.password:
            raise ValueError("password is required when email is provided")
        
        if self.password and not self.email:
            raise ValueError("email is required when password is provided")
    
    @classmethod
    def from_dict(cls, config_dict: dict) -> "ClientConfig":
        """Create configuration from dictionary.
        
        Useful for loading configuration from JSON/YAML files.
        
        Args:
            config_dict: Dictionary with configuration parameters.
            
        Returns:
            ClientConfig instance.
            
        Example:
            >>> import json
            >>> with open('config.json') as f:
            ...     config_dict = json.load(f)
            >>> config = ClientConfig.from_dict(config_dict)
        """
        return cls(**{
            k: v for k, v in config_dict.items()
            if k in cls.__dataclass_fields__
        })
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary.
        
        Useful for saving configuration to JSON/YAML files.
        
        Returns:
            Dictionary with configuration parameters.
        """
        return {
            "base_url": self.base_url,
            "email": self.email,
            "auto_auth": self.auto_auth,
            "max_retries": self.max_retries,
            "request_timeout": self.request_timeout,
            "server_error_cooldown": self.server_error_cooldown,
            "token_refresh_buffer": self.token_refresh_buffer,
            "enable_logging": self.enable_logging,
            "log_level": self.log_level,
        }
