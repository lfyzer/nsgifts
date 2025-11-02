"""IP whitelist management."""

from typing import Any, Dict

from ..enums import IPWhitelistEndpoint, HTTPRequestType
from ..models import (
    IPWhitelistRequest,
    IPWhitelistAddResponse,
    IPWhitelistRemoveResponse
)


class IPWhitelistMethods:
    """Manage IP whitelist for security."""

    def __init__(self, client):
        """Initialize with client reference.
        
        Args:
            client: Main NSGiftsClient instance.
        """

        self._client = client


    async def add_ip_to_whitelist(self, ip: str) -> IPWhitelistAddResponse:
        """Add IP to whitelist.
        
        Args:
            ip (str): IP address to allow access from.
            
        Returns:
            IPWhitelistAddResponse: IP address affected. Access via
                response.status, response.added.
        """

        data = IPWhitelistRequest(ip=ip).model_dump()

        result = await self._client._make_authenticated_request(
            HTTPRequestType.POST, 
            IPWhitelistEndpoint.ADD_IP, 
            json_data=data
        )

        return IPWhitelistAddResponse(**result)


    async def remove_ip_from_whitelist(
            self,
            ip: str
    ) -> IPWhitelistRemoveResponse:
        """Remove IP from whitelist.
        
        Args:
            ip (str): IP address to remove from whitelist.
                
        Returns:
            IPWhitelistRemoveResponse: IP address affected. Access via
                response.status, response.removed.
        """

        data = IPWhitelistRequest(ip=ip).model_dump()

        result = await self._client._make_authenticated_request(
            HTTPRequestType.POST,
            IPWhitelistEndpoint.REMOVE_IP,
            json_data=data,
        )

        return IPWhitelistRemoveResponse(**result)


    async def list_whitelist_ips(self) -> Dict[str, Any]:
        """Get all whitelisted IPs.
        
        Returns:
            Dict[str, Any]: List of whitelisted IP addresses.
        """

        return await self._client._make_authenticated_request(
            HTTPRequestType.POST,
            IPWhitelistEndpoint.LIST_IPS
        )