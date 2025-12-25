from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.product import ProductCategory


class ProductImageCreate(BaseModel):
    url: str
    alt_text: Optional[str] = None
    is_primary: bool = False
    sort_order: int = 0


class ProductImageResponse(ProductImageCreate):
    id: str

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    short_description: Optional[str] = None
    category: ProductCategory
    subcategory: Optional[str] = None
    brand: Optional[str] = None
    price: float = Field(..., gt=0)
    compare_at_price: Optional[float] = None
    sku: str
    stock_quantity: int = Field(default=0, ge=0)
    weight: Optional[float] = None
    dimensions: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    material: Optional[str] = None
    return_window_days: int = 30
    is_returnable: bool = True


class ProductCreate(ProductBase):
    images: List[ProductImageCreate] = []


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    category: Optional[ProductCategory] = None
    subcategory: Optional[str] = None
    brand: Optional[str] = None
    price: Optional[float] = None
    compare_at_price: Optional[float] = None
    stock_quantity: Optional[int] = None
    weight: Optional[float] = None
    dimensions: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    material: Optional[str] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    return_window_days: Optional[int] = None
    is_returnable: Optional[bool] = None


class ProductResponse(ProductBase):
    id: str
    slug: str
    seller_id: str
    is_active: bool
    is_featured: bool
    total_sold: int
    total_returned: int
    view_count: int
    return_rate: float
    avg_rating: float
    review_count: int
    discount_percentage: int
    in_stock: bool
    primary_image: str
    images: List[ProductImageResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    id: str
    name: str
    slug: str
    category: ProductCategory
    price: float
    compare_at_price: Optional[float] = None
    discount_percentage: int
    avg_rating: float
    review_count: int
    in_stock: bool
    primary_image: str
    seller_id: str

    class Config:
        from_attributes = True


class ProductSearchParams(BaseModel):
    query: Optional[str] = None
    category: Optional[ProductCategory] = None
    subcategory: Optional[str] = None
    brand: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_rating: Optional[float] = None
    in_stock_only: bool = False
    sort_by: str = "relevance"  # relevance, price_low, price_high, rating, newest
    page: int = 1
    per_page: int = 20
