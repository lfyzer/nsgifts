import uuid
from typing import Any, Dict, Optional

from ..enums import HTTPRequestType, OrdersEndpoint
from ..models import CreateOrder, PayOrder


class OrderMethods:
    def __init__(self, client):
        self._client = client

    async def create_order(
        self,
        service_id: int,
        quantity: float,
        custom_id: Optional[str] = None,
        data: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not custom_id:
            custom_id = str(uuid.uuid4())

        order_data = CreateOrder(
            service_id=service_id,
            quantity=quantity,
            custom_id=custom_id,
            data=data,
        ).model_dump(exclude_none=True)

        return await self._client._make_authenticated_request(
            HTTPRequestType.POST, 
            OrdersEndpoint.CREATE_ORDER, 
            json_data=order_data
        )

    async def pay_order(self, custom_id: str) -> Dict[str, Any]:
        data = PayOrder(custom_id=custom_id).model_dump()
        return await self._client._make_authenticated_request(
            HTTPRequestType.POST, 
            OrdersEndpoint.PAY_ORDER, 
            json_data=data
        )

    async def get_order_info(self, custom_id: str) -> Dict[str, Any]:
        data = PayOrder(custom_id=custom_id).model_dump()
        return await self._client._make_authenticated_request(
            HTTPRequestType.POST, 
            OrdersEndpoint.GET_ORDER_INFO, 
            json_data=data
        )