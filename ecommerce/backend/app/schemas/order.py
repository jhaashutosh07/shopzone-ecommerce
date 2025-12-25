from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.order import OrderStatus, PaymentStatus


class OrderItemResponse(BaseModel):
    id: str
    product_id: str
    product_name: str
    product_image: Optional[str] = None
    product_sku: str
    unit_price: float
    quantity: int
    total_price: float
    selected_size: Optional[str] = None
    selected_color: Optional[str] = None
    return_window_days: int
    is_returned: bool
    can_return: bool

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    address_id: str
    payment_method: str = "cod"  # cod, card, upi, netbanking
    customer_notes: Optional[str] = None


class OrderResponse(BaseModel):
    id: str
    order_number: str
    user_id: str
    status: OrderStatus
    payment_status: PaymentStatus
    subtotal: float
    tax: float
    shipping_fee: float
    discount: float
    total: float
    payment_method: Optional[str] = None
    shipping_name: str
    shipping_phone: str
    shipping_address: str
    shipping_city: str
    shipping_state: str
    shipping_postal_code: str
    tracking_number: Optional[str] = None
    carrier: Optional[str] = None
    items: List[OrderItemResponse]
    item_count: int
    can_cancel: bool
    can_return: bool
    created_at: datetime
    confirmed_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    id: str
    order_number: str
    status: OrderStatus
    payment_status: PaymentStatus
    total: float
    item_count: int
    created_at: datetime
    first_item_image: Optional[str] = None
    first_item_name: Optional[str] = None

    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    status: OrderStatus
    tracking_number: Optional[str] = None
    carrier: Optional[str] = None
    admin_notes: Optional[str] = None
