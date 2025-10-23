from typing import Any, Dict, List, Optional, Union

from ..enums import SteamRegion, HTTPRequestType, SteamEndpoint
from ..models import (
    PayOrder,
    SteamGiftOrder,
    SteamGiftOrderCalculate, 
    SteamRubCalculate,
)


class SteamMethods:
    def __init__(self, client):
        self._client = client

    async def calculate_steam_amount(self, amount: int) -> Dict[str, Any]:
        data = SteamRubCalculate(amount=amount).model_dump()
        return await self._client._make_authenticated_request(
            HTTPRequestType.POST, 
            SteamEndpoint.CALCULATE_AMOUNT, 
            json_data=data
        )

    async def get_steam_currency_rate(self) -> Dict[str, Any]:
        return await self._client._make_authenticated_request(
            HTTPRequestType.POST, 
            SteamEndpoint.GET_CURRENCY_RATE
        )

    async def calculate_steam_gift(
        self, 
        sub_id: int, 
        region: Union[SteamRegion, str]
    ) -> Dict[str, Any]:
        data = SteamGiftOrderCalculate(
            sub_id=sub_id, 
            region=region
        ).model_dump(by_alias=True)
        return await self._client._make_authenticated_request(
            HTTPRequestType.POST, 
            SteamEndpoint.CALCULATE_GIFT, 
            json_data=data
        )

    async def create_steam_gift_order(
        self,
        friend_link: str,
        sub_id: int,
        region: Union[SteamRegion, str],
        gift_name: Optional[str] = None,
        gift_description: Optional[str] = None,
    ) -> Dict[str, Any]:
        data = SteamGiftOrder(
            friend_link=friend_link,
            sub_id=sub_id,  
            region=region,
            gift_name=gift_name,
            gift_description=gift_description,
        ).model_dump(exclude_none=True, by_alias=True)

        return await self._client._make_authenticated_request(
            HTTPRequestType.POST,
            SteamEndpoint.CREATE_GIFT_ORDER,
            json_data=data,
        )

    async def pay_steam_gift_order(self, custom_id: str) -> Dict[str, Any]:
        data = PayOrder(custom_id=custom_id).model_dump()
        return await self._client._make_authenticated_request(
            HTTPRequestType.POST, 
            SteamEndpoint.PAY_GIFT_ORDER, 
            json_data=data
        )

    async def get_steam_apps(self) -> List[Dict[str, Any]]:
        return await self._client._make_authenticated_request(
            HTTPRequestType.POST, 
            SteamEndpoint.GET_APPS
        )