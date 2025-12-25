from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ReviewCreate(BaseModel):
    product_id: str
    order_id: Optional[str] = None
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = None
    content: Optional[str] = None
    images: Optional[List[str]] = None


class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = None
    content: Optional[str] = None


class ReviewResponse(BaseModel):
    id: str
    user_id: str
    product_id: str
    rating: int
    title: Optional[str] = None
    content: Optional[str] = None
    images: Optional[str] = None
    is_verified_purchase: bool
    helpful_count: int
    not_helpful_count: int
    seller_response: Optional[str] = None
    seller_responded_at: Optional[datetime] = None
    created_at: datetime
    user_name: str
    user_avatar: Optional[str] = None

    class Config:
        from_attributes = True


class ReviewSummary(BaseModel):
    avg_rating: float
    total_reviews: int
    rating_distribution: dict  # {5: 100, 4: 50, 3: 20, 2: 10, 1: 5}


class SellerResponseCreate(BaseModel):
    response: str
