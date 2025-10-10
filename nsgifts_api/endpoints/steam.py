"""Steam operations - gifts, currency, pricing."""

from typing import Any, Dict, List, Optional, Union

from ..models import (
    PayOrder,
    Region,
    SteamGiftOrder,
    SteamGiftOrderCalculate, 
    SteamRubCalculate,
)


class SteamEndpoints:
    """Steam operations like sending gifts and checking prices."""
    
    BASE_PATH_STEAM = "/api/v1/steam"
    BASE_PATH_GIFT = "/api/v1/steam_gift"
    
    @staticmethod
    def get_endpoints() -> Dict[str, str]:
        """Get Steam API endpoints.
        
        Returns:
            Dict[str, str]: Endpoint URLs for Steam operations.
        """
        return {
            "calculate_steam_amount":
                f"{SteamEndpoints.BASE_PATH_STEAM}/get_amount",
            "get_steam_currency_rate":
                f"{SteamEndpoints.BASE_PATH_STEAM}/get_currency_rate",
            "calculate_steam_gift":
                f"{SteamEndpoints.BASE_PATH_GIFT}/calculate",
            "create_steam_gift_order":
                f"{SteamEndpoints.BASE_PATH_GIFT}/create_order",
            "pay_steam_gift_order":
                f"{SteamEndpoints.BASE_PATH_GIFT}/pay_order",
            "get_steam_apps":
                f"{SteamEndpoints.BASE_PATH_GIFT}/get_apps",
        }

    def __init__(self, client):
        """Initialize with client reference.
        
        Args:
            client: Main NSGiftsClient instance.
        """
        self._client = client

    async def calculate_steam_amount(self, amount: int) -> Dict[str, Any]:
        """Calculate Steam amount from rubles.
        
        Shows how much Steam wallet money you get for your rubles.
        
        Args:
            amount (int): Rubles to convert.
                
        Returns:
            Dict[str, Any]: Calculation with exchange rates and fees.
        """
        data = SteamRubCalculate(amount=amount).model_dump()
        return await self._client._make_authenticated_request(
            "POST", 
            self.get_endpoints()["calculate_steam_amount"], 
            json_data=data
        )

    async def get_steam_currency_rate(self) -> Dict[str, Any]:
        """Get current Steam exchange rates.
        
        Returns:
            Dict[str, Any]: Current currency rates.
        """
        return await self._client._make_authenticated_request(
            "POST", 
            self.get_endpoints()["get_steam_currency_rate"]
        )

    async def calculate_steam_gift(
        self, 
        sub_id: int, 
        region: Union[Region, str]
    ) -> Dict[str, Any]:
        """Calculate Steam gift price.
        
        Check how much it costs to gift a game before ordering.
        
        Note:
            Rate limited to 1 request per 60 seconds.

        Args:
            sub_id (int): Steam package ID (find it in Steam store URLs).
            region (Union[Region, str]): Target region ('ru', 'kz', 'ua').
                
        Returns:
            Dict[str, Any]: Price and availability info for the gift.
        """
        data = SteamGiftOrderCalculate(
            sub_id=sub_id, 
            region=region
        ).model_dump()
        return await self._client._make_authenticated_request(
            "POST", 
            self.get_endpoints()["calculate_steam_gift"], 
            json_data=data
        )

    async def create_steam_gift_order(
        self,
        friend_link: str,
        sub_id: int,
        region: Union[Region, str],
        gift_name: Optional[str] = None,
        gift_description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create Steam gift order.
        
        Send a Steam game as a gift to your friend.
        
        Args:
            friend_link (str): Your friend's Steam profile URL.
            sub_id (int): Steam package ID to gift.
            region (Union[Region, str]): Target region ('ru', 'kz', 'ua').
            gift_name (Optional[str]): Custom gift title (optional).
            gift_description (Optional[str]): Personal message (optional).
                
        Returns:
            Dict[str, Any]: Order details and tracking info.
        """
        data = SteamGiftOrder(
            friend_link=friend_link,
            sub_id=sub_id,
            region=region,
            gift_name=gift_name,
            gift_description=gift_description,
        ).model_dump(exclude_none=True)

        return await self._client._make_authenticated_request(
            "POST",
            self.get_endpoints()["create_steam_gift_order"],
            json_data=data,
        )

    async def pay_steam_gift_order(self, custom_id: str) -> Dict[str, Any]:
        """Pay for Steam gift order.
        
        Complete payment and send the gift to your friend.
        
        Args:
            custom_id (str): Order ID from create_steam_gift_order.
                
        Returns:
            Dict[str, Any]: Payment status and delivery info.
        """
        data = PayOrder(custom_id=custom_id).model_dump()
        return await self._client._make_authenticated_request(
            "POST", 
            self.get_endpoints()["pay_steam_gift_order"], 
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
            APIAuthenticationError: If not authenticated or token expired.
            APIServerError: If server error occurs.
            APIConnectionError: If connection fails.
            APITimeoutError: If request times out.
        """
        return await self._client._make_authenticated_request(
            "POST", 
            self.get_endpoints()["get_steam_apps"]
        )
