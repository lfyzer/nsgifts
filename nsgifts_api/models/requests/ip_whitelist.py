"""Common API request models."""

import re

from pydantic import BaseModel, Field, field_validator


class IPWhitelistRequest(BaseModel):
    """IP whitelist management request.
    
    Attributes:
        ip (str): IP address to add or remove from whitelist.
    """
    
    ip: str = Field(..., min_length=7, max_length=45)
    
    @field_validator('ip')
    @classmethod
    def validate_ip_address(cls, v: str) -> str:
        """Validate IP address format.
        
        Args:
            v: IP address string to validate.
            
        Returns:
            Validated IP address string.
            
        Raises:
            ValueError: If IP address format is invalid.
        """
        ip_pattern = re.compile(
            r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
            r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        )
        if not ip_pattern.match(v):
            raise ValueError('Invalid IP address format')
        return v
