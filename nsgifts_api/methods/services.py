"""Services - browse catalog, categories, products."""

from typing import Any, Dict, List

from ..enums import ServicesEndpoint, HTTPRequestType
from ..models import CategoryRequest


class ServicesMethods:
    """Browse services and categories."""

    def __init__(self, client):
        """Initialize with client reference.
        
        Args:
            client: Main NSGiftsClient instance.
        """

        self._client = client


    async def get_all_services(self) -> Dict[str, Any]:
        """Get all available services.
        
        Returns complete service catalog with categories and pricing.
        
        Returns:
            Dict[str, Any]: Raw API response with categories and services.
                Structure: {"categories": [{"category_name": str, 
                "category_id": int, "services": [...]}]}
        """

        return await self._client._make_authenticated_request(
            HTTPRequestType.POST,
            ServicesEndpoint.GET_ALL_SERVICES
        )


    async def get_categories(self) -> List[Dict[str, Any]]:
        """Get service categories.
        
        Returns:
            List[Dict[str, Any]]: List of all available categories.
        """

        return await self._client._make_authenticated_request(
            HTTPRequestType.POST,
            ServicesEndpoint.GET_CATEGORIES
        )


    async def get_services_by_category(
        self, category_id: int
    ) -> List[Dict[str, Any]]:
        """Get services from specific category.
        
        Args:
            category_id (int): Category ID to filter by.
            
        Returns:
            List[Dict[str, Any]]: List of services in the specified category.
        """

        data = CategoryRequest(category_id=category_id).model_dump()
        result = await self._client._make_authenticated_request(
            HTTPRequestType.POST,
            ServicesEndpoint.GET_SERVICES_BY_CATEGORY, 
            json_data=data
        )
        
        return result if isinstance(result, list) else []