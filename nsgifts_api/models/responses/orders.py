"""Order API response models."""

from typing import Optional, List

from pydantic import BaseModel, ConfigDict


class OrderResponse(BaseModel):
    """Order creation/info response.
    
    Attributes:
        custom_id (str): Custom order ID.
        status (int): Order status code.
        service_id (int): Service ID.
        quantity (float): Order quantity.
        total (float): Total cost.
        date (str): Order date.
        data (Optional[str]): Additional order data.
        pin_code (Optional[str]): PIN code if applicable.
        trade_link (Optional[str]): Steam trade link if applicable.
        complete_date (Optional[str]): Completion date.
    """

    model_config = ConfigDict(extra="allow")

    custom_id: str
    status: int
    service_id: int
    quantity: float
    total: float
    date: str
    data: Optional[str] = None
    pin_code: Optional[List[str]] = None
    trade_link: Optional[str] = None
    complete_date: Optional[str] = None

class PaymentResponse(BaseModel):
    """Order payment response.
    
    Attributes:
        custom_id (str): Custom order ID.
        status (int): Payment status code.
        new_balance (str): User's new balance after payment.
        msg (str): Payment status message.
        pins (Optional[List[str]]): List of PIN codes if applicable.
    """

    model_config = ConfigDict(extra="allow")

    custom_id: str
    status: int
    new_balance: str
    msg: str
    pins: Optional[List[str]] = None    


class OrderInfoResponse(BaseModel):
    """Detailed order information response.
    
    Attributes:
        custom_id (str): Custom order ID.
        status (int): Order status code.
        status_message (str): Human-readable status message.
        product (Optional[str]): Product name if applicable.
        quantity (Optional[float]): Order quantity if applicable.
        total_price (Optional[float]): Total price if applicable.
        data (Optional[str]): Additional order data.
        pins (Optional[List[str]]): List of PIN codes if applicable.
        trade_link (Optional[str]): Steam trade link if applicable.
        complete_date (Optional[str]): Completion date.
    """

    model_config = ConfigDict(extra="allow")

    custom_id: str
    status: int
    status_message: str
    product: Optional[str] = None
    quantity: Optional[float] = None
    total_price: Optional[float] = None
    data: Optional[str] = None
    pins: Optional[List[str]] = None
    trade_link: Optional[str] = None
    complete_date: Optional[str] = None