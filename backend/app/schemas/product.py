from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from app.models.product import PriceTier, ProductCategory


class ProductBase(BaseModel):
    external_product_id: str = Field(..., min_length=1, max_length=255)
    name: str = Field(..., min_length=1, max_length=255)


class ProductCreate(ProductBase):
    category: ProductCategory = ProductCategory.OTHER
    price: float = Field(..., gt=0)
    price_tier: Optional[PriceTier] = None  # Auto-calculated if not provided
    custom_return_window: Optional[int] = Field(None, ge=1, le=365)
    total_sold: int = Field(default=0, ge=0)
    total_returned: int = Field(default=0, ge=0)


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[ProductCategory] = None
    price: Optional[float] = Field(None, gt=0)
    custom_return_window: Optional[int] = Field(None, ge=1, le=365)
    total_sold: Optional[int] = Field(None, ge=0)
    total_returned: Optional[int] = Field(None, ge=0)


class ProductResponse(ProductBase):
    id: str
    merchant_id: str
    category: ProductCategory
    price: float
    price_tier: PriceTier
    custom_return_window: Optional[int]
    total_sold: int
    total_returned: int
    return_rate: float
    created_at: datetime

    class Config:
        from_attributes = True


class ProductSync(BaseModel):
    """Schema for bulk syncing product data from merchant's platform."""
    products: List[ProductCreate]


class ProductSyncResponse(BaseModel):
    created: int
    updated: int
    failed: int
    errors: List[str] = []
