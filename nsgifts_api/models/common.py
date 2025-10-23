from pydantic import BaseModel, Field, validator
import re


class PayOrder(BaseModel):
    custom_id: str = Field(..., min_length=1, max_length=255)


class IPWhitelistRequest(BaseModel):
    ip: str = Field(..., min_length=7, max_length=45)
    
    @validator('ip')
    def validate_ip_address(cls, v):
        ip_pattern = re.compile(
            r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
            r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        )
        if not ip_pattern.match(v):
            raise ValueError('Invalid IP address format')
        return v
