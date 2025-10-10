"""IP whitelist management."""

from typing import Any, Dict

from ..models import IPWhitelistRequest


class IPWhitelistEndpoints:
    """Manage IP whitelist for security."""
    
    BASE_PATH = "/api/v1/ip-whitelist"
    
    @staticmethod
    def get_endpoints() -> Dict[str, str]:
        """Get IP whitelist endpoint URLs.
        
        Returns:
            Dict[str, str]: IP whitelist endpoint URLs.
        """
        return {
            "add_ip_to_whitelist": (
                f"{IPWhitelistEndpoints.BASE_PATH}/add"
            ),
            "remove_ip_from_whitelist": (
                f"{IPWhitelistEndpoints.BASE_PATH}/remove"
            ),
            "list_whitelist_ips": (
                f"{IPWhitelistEndpoints.BASE_PATH}/list"
            ),
        }

    def __init__(self, client):
        """Initialize with client reference.
        
        Args:
            client: Main NSGiftsClient instance.
        """
        self._client = client

    async def add_ip_to_whitelist(self, ip: str) -> Dict[str, Any]:
        """Add IP to whitelist.
        
        Args:
            ip (str): IP address to allow access from.
            
        Returns:
            Dict[str, Any]: Operation result.
        """
        data = IPWhitelistRequest(ip=ip).model_dump()
        return await self._client._make_authenticated_request(
            "POST", 
            self.get_endpoints()["add_ip_to_whitelist"], 
            json_data=data
        )

    async def remove_ip_from_whitelist(self, ip: str) -> Dict[str, Any]:
        """Remove IP from whitelist.
        
        Args:
            ip (str): IP address to remove from whitelist.
                
        Returns:
            Dict[str, Any]: Operation result.
        """
        data = IPWhitelistRequest(ip=ip).model_dump()
        return await self._client._make_authenticated_request(
            "POST",
            self.get_endpoints()["remove_ip_from_whitelist"],
            json_data=data,
        )

    async def list_whitelist_ips(self) -> Dict[str, Any]:
        """Get all whitelisted IPs.
        
        Returns:
            Dict[str, Any]: List of whitelisted IP addresses.
        """
        return await self._client._make_authenticated_request(
            "POST", 
            self.get_endpoints()["list_whitelist_ips"]
        )
