from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CartItemCreate(BaseModel):
    product_id: str
    quantity: int = Field(default=1, ge=1)
    selected_size: Optional[str] = None
    selected_color: Optional[str] = None


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., ge=1)


class CartItemResponse(BaseModel):
    id: str
    product_id: str
    quantity: int
    selected_size: Optional[str] = None
    selected_color: Optional[str] = None
    unit_price: float
    total_price: float
    product_name: str
    product_image: str
    product_in_stock: bool
    product_stock_quantity: int

    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    id: str
    items: List[CartItemResponse]
    total_items: int
    subtotal: float
    tax: float
    total: float

    class Config:
        from_attributes = True


class CartSummary(BaseModel):
    total_items: int
    subtotal: float
    tax: float
    shipping_fee: float
    discount: float
    total: float
