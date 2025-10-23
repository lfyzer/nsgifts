from typing import Any, Dict

from ..enums import HTTPRequestType, IPWhitelistEndpoint
from ..models import IPWhitelistRequest


class IPWhitelistMethods:
    def __init__(self, client):
        self._client = client

    async def add_ip_to_whitelist(self, ip: str) -> Dict[str, Any]:
        data = IPWhitelistRequest(ip=ip).model_dump()
        return await self._client._make_authenticated_request(
            HTTPRequestType.POST, 
            IPWhitelistEndpoint.ADD_IP, 
            json_data=data
        )

    async def remove_ip_from_whitelist(self, ip: str) -> Dict[str, Any]:
        data = IPWhitelistRequest(ip=ip).model_dump()
        return await self._client._make_authenticated_request(
            HTTPRequestType.POST,
            IPWhitelistEndpoint.REMOVE_IP,
            json_data=data,
        )

    async def list_whitelist_ips(self) -> Dict[str, Any]:
        return await self._client._make_authenticated_request(
            HTTPRequestType.POST, 
            IPWhitelistEndpoint.LIST_IPS
        )