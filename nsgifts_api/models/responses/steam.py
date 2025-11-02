"""Steam API response models."""

from pydantic import BaseModel, Field, ConfigDict


class SteamAmountResponse(BaseModel):
    """Steam amount calculation response.
    
    Attributes:
        exchange_rate (float): USD/RUB exchange rate.
        usd_price (float): Price in USD.
    """
    
    exchange_rate: float
    usd_price: float


class SteamCurrencyRateResponse(BaseModel):
    """Steam currency rate response.
    
    Attributes:
        date (str): Date of the rate.
        rub_usd (str): RUB to USD exchange rate.
        kzt_usd (str): KZT to USD exchange rate.
        uah_usd (str): UAH to USD exchange rate.
    """
    
    model_config = ConfigDict(populate_by_name=True)
    
    date: str
    rub_usd: str = Field(alias="rub/usd")
    kzt_usd: str = Field(alias="kzt/usd")
    uah_usd: str = Field(alias="uah/usd")


class SteamGiftCalculateResponse(BaseModel):
    """Steam gift calculation response.
    
    Attributes:
        sub_id (int): Steam package ID.
        region (str): Region code.
        price (float): Calculated price in USDT.
    """
    
    sub_id: int
    region: str
    price: float


class SteamGiftOrderResponse(BaseModel):
    """Steam gift order response.
    
    Attributes:
        custom_id (str): Custom order ID.
        status (int): Order status code.
        service_id (int): Service ID.
        quantity (int): Quantity ordered.
        total (float): Total price.
        date (str): Order date.
    """
    
    custom_id: str
    status: int
    service_id: int
    quantity: int
    total: float
    date: str