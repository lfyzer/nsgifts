"""Services - browse catalog, categories, products."""

from typing import Any, Dict

from ..models import CategoryRequest


class ServicesMethods:
    """Browse services and categories."""
    
    BASE_PATH = "/api/v1/products"
    
    @staticmethod
    def get_endpoints() -> Dict[str, str]:
        """Get service endpoint URLs.
        
        Returns:
            Dict[str, str]: Service endpoint URLs.
        """
        return {
            "get_all_services": (
                f"{ServicesMethods.BASE_PATH}/get_all_services"
            ),
            "get_categories": f"{ServicesMethods.BASE_PATH}/get_categories",
            "get_services_by_category": (
                f"{ServicesMethods.BASE_PATH}/get_services"
            ),
        }

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
            Dict[str, Any]: All services organized by categories.
        """
        return await self._client._make_authenticated_request(
            "POST", 
            self.get_endpoints()["get_all_services"]
        )

    async def get_categories(self) -> Dict[str, Any]:
        """Get service categories.
        
        Returns:
            Dict[str, Any]: List of all available categories.
        """
        return await self._client._make_authenticated_request(
            "POST", 
            self.get_endpoints()["get_categories"]
        )

    async def get_services_by_category(
        self, category_id: int
    ) -> Dict[str, Any]:
        """Get services from specific category.
        
        Args:
            category_id (int): Category ID to filter by.
            
        Returns:
            Dict[str, Any]: Services in the specified category.
        """
        data = CategoryRequest(category_id=category_id).model_dump()
        return await self._client._make_authenticated_request(
            "POST", 
            self.get_endpoints()["get_services_by_category"], 
            json_data=data
        )
