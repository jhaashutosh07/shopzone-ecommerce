from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class BuyerBase(BaseModel):
    external_buyer_id: str = Field(..., min_length=1, max_length=255)


class BuyerCreate(BuyerBase):
    total_orders: int = Field(default=0, ge=0)
    total_returns: int = Field(default=0, ge=0)
    total_reviews: int = Field(default=0, ge=0)
    avg_review_score: float = Field(default=0.0, ge=0, le=5)
    total_spend: float = Field(default=0.0, ge=0)
    account_created_at: Optional[datetime] = None
    last_order_at: Optional[datetime] = None


class BuyerUpdate(BaseModel):
    total_orders: Optional[int] = Field(None, ge=0)
    total_returns: Optional[int] = Field(None, ge=0)
    total_reviews: Optional[int] = Field(None, ge=0)
    avg_review_score: Optional[float] = Field(None, ge=0, le=5)
    total_spend: Optional[float] = Field(None, ge=0)
    last_order_at: Optional[datetime] = None


class BuyerResponse(BuyerBase):
    id: str
    merchant_id: str
    total_orders: int
    total_returns: int
    total_reviews: int
    avg_review_score: float
    total_spend: float
    account_created_at: Optional[datetime]
    last_order_at: Optional[datetime]
    created_at: datetime
    return_rate: float

    class Config:
        from_attributes = True


class BuyerSync(BaseModel):
    """Schema for bulk syncing buyer data from merchant's platform."""
    buyers: List[BuyerCreate]


class BuyerSyncResponse(BaseModel):
    created: int
    updated: int
    failed: int
    errors: List[str] = []
