from pydantic import BaseModel, ConfigDict, Field
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
    # model_version collides with pydantic's protected "model_" namespace
    model_config = ConfigDict(protected_namespaces=(), from_attributes=True)

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
    risk_flags: Optional[List[dict]]
    confidence: Optional[float]
    explanation: Optional[List[dict]] = None
    model_version: Optional[int] = None
    decision: ReturnDecision
    decided_at: Optional[datetime]
    decided_by: Optional[str]
    days_since_order: int
    created_at: datetime


class ReturnRequestListResponse(BaseModel):
    items: List[ReturnRequestResponse]
    total: int
    page: int
    per_page: int
