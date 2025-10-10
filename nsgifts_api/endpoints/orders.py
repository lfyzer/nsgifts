"""Order management - create, pay, track."""

import uuid
from typing import Any, Dict, Optional

from ..models import CreateOrder, PayOrder


class OrderEndpoints:
    """Handle order operations."""
    
    BASE_PATH = "/api/v1"
    
    @staticmethod
    def get_endpoints() -> Dict[str, str]:
        """Get order endpoint URLs.
        
        Returns:
            Order endpoint URLs.
        """
        return {
            "create_order": f"{OrderEndpoints.BASE_PATH}/create_order",
            "pay_order": f"{OrderEndpoints.BASE_PATH}/pay_order",
            "get_order_info": f"{OrderEndpoints.BASE_PATH}/order_info",
        }

    def __init__(self, client):
        """Initialize with client reference.
        
        Args:
            client: Main NSGiftsClient instance.
        """
        self._client = client

    async def create_order(
        self,
        service_id: int,
        quantity: float,
        custom_id: Optional[str] = None,
        data: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create new order.
        
        Order needs to be paid separately with pay_order().
        
        Args:
            service_id (int): Service ID from catalog.
            quantity (float): How much to order.
            custom_id (Optional[str]): Your order ID (auto-generated if not
                provided).
            data (Optional[str]): Extra info like Steam username (optional).
                
        Returns:
            Order creation details.
        """
        if not custom_id:
            custom_id = str(uuid.uuid4())

        order_data = CreateOrder(
            service_id=service_id,
            quantity=quantity,
            custom_id=custom_id,
            data=data,
        ).model_dump(exclude_none=True)

        return await self._client._make_authenticated_request(
            "POST", 
            self.get_endpoints()["create_order"], 
            json_data=order_data
        )

    async def pay_order(self, custom_id: str) -> Dict[str, Any]:
        """Process payment for an existing order.
        
        Initiates payment processing for an order that was previously 
        created. The order must exist and be in a payable state.
        
        Args:
            custom_id (str): The custom identifier of the order to pay for.
                This is either the custom_id provided during order creation
                or the auto-generated UUID4.
                
        Returns:
            Dict[str, Any]: Payment response containing transaction details
                and payment status information.
                
        Raises:
            APIAuthenticationError: If not authenticated or token expired.
            APIClientError: If custom_id is invalid or order cannot be
                paid.
            APIServerError: If server error occurs.
            APIConnectionError: If connection fails.
            APITimeoutError: If request times out.
        """
        data = PayOrder(custom_id=custom_id).model_dump()
        return await self._client._make_authenticated_request(
            "POST", 
            self.get_endpoints()["pay_order"], 
            json_data=data
        )

    async def get_order_info(self, custom_id: str) -> Dict[str, Any]:
        """Retrieve detailed information about an order.
        
        Returns comprehensive details about an order including status,
        progress, completion information, and any relevant order data.
        
        Args:
            custom_id (str): The custom identifier of the order to query.
                This is either the custom_id provided during order creation
                or the auto-generated UUID4.
                
        Returns:
            Dict[str, Any]: Order information containing:
                - Order status and current state
                - Creation and completion timestamps
                - Service details and quantity
                - Payment information
                - Progress updates and completion data
                
        Raises:
            APIAuthenticationError: If not authenticated or token expired.
            APIClientError: If custom_id is invalid or order not found.
            APIServerError: If server error occurs.
            APIConnectionError: If connection fails.
            APITimeoutError: If request times out.
        """
        data = PayOrder(custom_id=custom_id).model_dump()
        return await self._client._make_authenticated_request(
            "POST", 
            self.get_endpoints()["get_order_info"], 
            json_data=data
        )
