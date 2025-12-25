from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.return_request import ReturnStatus, ReturnReason


class ReturnRequestCreate(BaseModel):
    order_id: str
    order_item_id: str
    reason: ReturnReason
    reason_details: Optional[str] = None
    images: Optional[List[str]] = None


class ReturnRequestResponse(BaseModel):
    id: str
    return_number: str
    order_id: str
    order_item_id: str
    user_id: str
    reason: ReturnReason
    reason_details: Optional[str] = None
    status: ReturnStatus
    eligibility_score: Optional[float] = None
    risk_level: Optional[str] = None
    risk_flags: Optional[str] = None
    engine_recommendation: Optional[str] = None
    engine_confidence: Optional[float] = None
    decision: Optional[str] = None
    decided_by: Optional[str] = None
    decision_notes: Optional[str] = None
    refund_amount: Optional[float] = None
    refund_method: Optional[str] = None
    pickup_date: Optional[datetime] = None
    pickup_slot: Optional[str] = None
    days_since_delivery: int
    created_at: datetime
    approved_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    refunded_at: Optional[datetime] = None

    # Include product details
    product_name: Optional[str] = None
    product_image: Optional[str] = None
    order_amount: Optional[float] = None

    class Config:
        from_attributes = True


class ReturnRequestListResponse(BaseModel):
    id: str
    return_number: str
    order_number: str
    status: ReturnStatus
    reason: ReturnReason
    eligibility_score: Optional[float] = None
    risk_level: Optional[str] = None
    engine_recommendation: Optional[str] = None
    product_name: str
    product_image: Optional[str] = None
    refund_amount: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ReturnDecisionUpdate(BaseModel):
    decision: str  # approved, rejected
    decision_notes: Optional[str] = None
    refund_amount: Optional[float] = None
    refund_method: Optional[str] = None


class SchedulePickup(BaseModel):
    pickup_address: str
    pickup_date: datetime
    pickup_slot: str  # morning, afternoon, evening


class ReturnEngineScore(BaseModel):
    """Response from Return Policy Engine"""
    score: float
    risk_level: str
    recommendation: str
    risk_flags: List[dict]
    confidence: float
    buyer_return_rate: Optional[float] = None
    days_since_order: int
    within_return_window: bool
    request_id: Optional[str] = None
