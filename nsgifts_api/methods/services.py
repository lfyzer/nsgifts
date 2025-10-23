from typing import Any, Dict

from ..enums import HTTPRequestType, ServicesEndpoint
from ..models import CategoryRequest


class ServicesMethods:
    def __init__(self, client):
        self._client = client

    async def get_all_services(self) -> Dict[str, Any]:
        return await self._client._make_authenticated_request(
            HTTPRequestType.POST, 
            ServicesEndpoint.GET_ALL_SERVICES
        )

    async def get_categories(self) -> Dict[str, Any]:
        return await self._client._make_authenticated_request(
            HTTPRequestType.POST, 
            ServicesEndpoint.GET_CATEGORIES
        )

    async def get_services_by_category(self, category_id: int) -> Dict[str, Any]:
        data = CategoryRequest(category_id=category_id).model_dump()
        return await self._client._make_authenticated_request(
            HTTPRequestType.POST, 
            ServicesEndpoint.GET_SERVICES_BY_CATEGORY, 
            json_data=data
        )