"""Order management - create, pay, track."""

import uuid
from typing import Optional

from ..enums import OrdersEndpoint, HTTPRequestType
from ..models import (
    CreateOrder,
    OrderResponse,
    PayOrder,
    OrderInfoResponse,
    PaymentResponse
)

class OrderMethods:
    """Handle order operations."""

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
    ) -> OrderResponse:

        """Create new order.

        Order needs to be paid separately with pay_order().

        Args:
            service_id (int): Service ID from catalog.
            quantity (float): How much to order.
            custom_id (Optional[str]): Your order ID (auto-generated if
                not provided).
            data (Optional[str]): Extra info like Steam username
                (optional).

        Returns:
            OrderResponse: Order creation details. Access via
                response.custom_id, response.status, response.service_id,
                response.quantity, response.total, response.date.
        """

        if not custom_id:
            custom_id = str(uuid.uuid4())

        order_data = CreateOrder(
            service_id=service_id,
            quantity=quantity,
            custom_id=custom_id,
            data=data,
        ).model_dump(exclude_none=True)

        result = await self._client._make_authenticated_request(
            HTTPRequestType.POST,
            OrdersEndpoint.CREATE_ORDER, 
            json_data=order_data
        )

        return OrderResponse(**result)


    async def pay_order(self, custom_id: str) -> PaymentResponse:
        """Process payment for an existing order.
        
        Initiates payment processing for an order that was previously 
        created. The order must exist and be in a payable state.
        
        Args:
            custom_id (str): The custom identifier of the order to pay
                for. This is either the custom_id provided during order
                creation or the auto-generated UUID4.
                
        Returns:
            PaymentResponse: Payment result details. Access via
                response.custom_id, response.status, response.new_balance,
                response.msg, response.pins.
                
        Raises:
            APIAuthenticationError: If not authenticated or token
                expired.
            APIClientError: If custom_id is invalid or order cannot be
                paid.
            APIServerError: If server error occurs.
            APIConnectionError: If connection fails.
            APITimeoutError: If request times out.
        """

        data = PayOrder(custom_id=custom_id).model_dump()

        result = await self._client._make_authenticated_request(
            HTTPRequestType.POST,
            OrdersEndpoint.PAY_ORDER,
            json_data=data
        )

        return PaymentResponse(**result)

    async def get_order_info(self, custom_id: str) -> OrderInfoResponse:
        """Retrieve detailed information about an order.
        
        Returns comprehensive details about an order including status,
        completion information, and any relevant order data.
        
        Args:
            custom_id (str): The custom identifier of the order to query.
                This is either the custom_id provided during order
                creation or the auto-generated UUID4.
                
        Returns:
            OrderInfoResponse: Detailed order information. Access via
                response.custom_id, response.status, response.status_message,
                response.product, response.quantity, response.total_price, etc.
                
        Raises:
            APIAuthenticationError: If not authenticated or token
                expired.
            APIClientError: If custom_id is invalid or order not found.
            APIServerError: If server error occurs.
            APIConnectionError: If connection fails.
            APITimeoutError: If request times out.
        """

        data = PayOrder(custom_id=custom_id).model_dump()
        result = await self._client._make_authenticated_request(
            HTTPRequestType.POST,
            OrdersEndpoint.GET_ORDER_INFO, 
            json_data=data
        )

        return OrderInfoResponse(**result)
