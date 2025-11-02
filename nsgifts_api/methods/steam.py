"""Steam operations - gifts, currency, pricing."""

from typing import Any, Dict, List, Optional, Union

from ..enums import Region, SteamEndpoint, HTTPRequestType
from ..models import (
    PayOrder,
    SteamAmountResponse,
    SteamCurrencyRateResponse,
    SteamGiftCalculateResponse,
    SteamGiftOrder,
    SteamGiftOrderCalculate,
    SteamGiftOrderResponse,
    SteamRubCalculate,
)


class SteamMethods:
    """Steam operations like sending gifts and checking prices."""

    def __init__(self, client):
        """Initialize with client reference.
        
        Args:
            client: Main NSGiftsClient instance.
        """

        self._client = client


    async def calculate_steam_amount(
        self, amount: int
    ) -> SteamAmountResponse:
        """Calculate Steam amount from rubles.
        
        Shows how much Steam wallet money you get for your rubles.
        
        Args:
            amount (int): Rubles to convert.
                
        Returns:
            SteamAmountResponse: Calculated Steam amount. Access via
                response.exchange_rate, response.usd_price.
        """

        data = SteamRubCalculate(amount=amount).model_dump()
        result = await self._client._make_authenticated_request(
            HTTPRequestType.POST,
            SteamEndpoint.CALCULATE_AMOUNT,
            json_data=data
        )

        return SteamAmountResponse(**result)


    async def get_steam_currency_rate(self) -> SteamCurrencyRateResponse:
        """Get current Steam exchange rates.
        
        Returns:
            SteamCurrencyRateResponse: Current currency rates. Access via
                response.date, response.rub_usd, response.kzt_usd,
                response.uah_usd.
        """

        result = await self._client._make_authenticated_request(
            HTTPRequestType.POST,
            SteamEndpoint.GET_CURRENCY_RATE
        )

        return SteamCurrencyRateResponse(**result)


    async def calculate_steam_gift(
        self, 
        sub_id: int, 
        region: Union[Region, str]
    ) -> SteamGiftCalculateResponse:
        """Calculate Steam gift price.
        
        Check how much it costs to gift a game before ordering.
        
        Note:
            Rate limited to 1 request per 30 seconds.

        Args:
            sub_id (int): Steam package ID (find it in Steam store URLs).
            region (Union[Region, str]): Target region ('ru', 'kz', 'ua').
                
        Returns:
            SteamGiftCalculateResponse: Price and availability info.
                Access via response.sub_id, response.region, response.price.
        """

        data = SteamGiftOrderCalculate(
            sub_id=sub_id, 
            region=region
        ).model_dump(by_alias=True)

        result = await self._client._make_authenticated_request(
            HTTPRequestType.POST,
            SteamEndpoint.CALCULATE_GIFT,
            json_data=data
        )

        return SteamGiftCalculateResponse(**result)


    async def create_steam_gift_order(
        self,
        friend_link: str,
        sub_id: int,
        region: Union[Region, str],
        gift_name: Optional[str] = None,
        gift_description: Optional[str] = None,
    ) -> SteamGiftOrderResponse:
        """Create Steam gift order.
        
        Send a Steam game as a gift to your friend.
        
        Args:
            friend_link (str): Your friend's Steam profile URL.
            sub_id (int): Steam package ID to gift.
            region (Union[Region, str]): Target region ('ru', 'kz', 'ua').
            gift_name (Optional[str]): Custom gift title (optional).
            gift_description (Optional[str]): Personal message (optional).
                
        Returns:
            SteamGiftOrderResponse: Order details. Access via
                response.custom_id, response.status, response.service_id,
                response.quantity, response.total, response.date.
        """

        data = SteamGiftOrder(
            friend_link=friend_link,
            sub_id=sub_id,
            region=region,
            gift_name=gift_name,
            gift_description=gift_description
        ).model_dump(exclude_none=True, by_alias=True)

        result = await self._client._make_authenticated_request(
            HTTPRequestType.POST,
            SteamEndpoint.CREATE_GIFT_ORDER,
            json_data=data,
        )

        return SteamGiftOrderResponse(**result)


    async def pay_steam_gift_order(self, custom_id: str) -> Dict[str, Any]:
        """Pay for Steam gift order.
        
        Complete payment and send the gift to your friend.
        
        Args:
            custom_id (str): Order ID from create_steam_gift_order.
                
        Returns:
            Dict[str, Any]: Payment status and delivery info.
        """

        data = PayOrder(custom_id=custom_id).model_dump(by_alias=True)
        return await self._client._make_authenticated_request(
            HTTPRequestType.POST,
            SteamEndpoint.PAY_GIFT_ORDER,
            json_data=data
        )


    async def get_steam_apps(self) -> List[Dict[str, Any]]:
        """Get all available Steam apps with Sub/Package ID prices.
        
        Returns Steam Sub/Package ID prices for regions (RU, KZ, UA).
        
        Note:
            Rate limited to 1 request per 60 seconds.
        
        Returns:
            List[Dict[str, Any]]: List of Steam apps with pricing info
                for different regions.
                
        Raises:
            APIAuthenticationError: If not authenticated or token
                expired.
            APIServerError: If server error occurs.
            APIConnectionError: If connection fails.
            APITimeoutError: If request times out.
        """

        return await self._client._make_authenticated_request(
            HTTPRequestType.POST,
            SteamEndpoint.GET_APPS
        )
