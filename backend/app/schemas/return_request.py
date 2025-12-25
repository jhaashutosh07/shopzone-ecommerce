from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from app.models.return_request import ReturnReason, ReturnDecision


class ReturnRequestBase(BaseModel):
    order_id: str = Field(..., min_length=1, max_length=255)
    reason: ReturnReason


class ReturnRequestCreate(ReturnRequestBase):
    buyer_id: str  # External buyer ID
    product_id: str  # External product ID
    order_date: datetime
    order_amount: float = Field(..., gt=0)
    reason_details: Optional[str] = None


class ReturnRequestUpdate(BaseModel):
    decision: ReturnDecision
    decided_by: Optional[str] = None


class ReturnRequestResponse(BaseModel):
    id: str
    merchant_id: str
    buyer_id: str
    product_id: str
    order_id: str
    order_date: datetime
    order_amount: float
    request_date: datetime
    reason: ReturnReason
    reason_details: Optional[str]
    eligibility_score: Optional[float]
    risk_level: Optional[str]
    risk_flags: Optional[List[str]]
    confidence: Optional[float]
    decision: ReturnDecision
    decided_at: Optional[datetime]
    decided_by: Optional[str]
    days_since_order: int
    created_at: datetime

    class Config:
        from_attributes = True


class ReturnRequestListResponse(BaseModel):
    items: List[ReturnRequestResponse]
    total: int
    page: int
    per_page: int
