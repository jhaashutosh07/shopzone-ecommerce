from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

from app.models.return_request import ReturnReason


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Recommendation(str, Enum):
    APPROVE = "APPROVE"
    REVIEW = "REVIEW"
    DENY = "DENY"


class RiskFlag(BaseModel):
    code: str
    description: str
    severity: str  # low, medium, high


class ScoreRequest(BaseModel):
    """Request to calculate return eligibility score."""
    buyer_id: str = Field(..., description="External buyer ID from merchant's system")
    product_id: str = Field(..., description="External product ID from merchant's system")
    order_id: str = Field(..., description="Order ID")
    order_date: datetime = Field(..., description="Date of original order")
    order_amount: float = Field(..., gt=0, description="Order amount")
    return_reason: ReturnReason = Field(..., description="Reason for return")
    reason_details: Optional[str] = Field(None, description="Additional details")


class ScoreResponse(BaseModel):
    """Response with return eligibility score and recommendation."""
    score: float = Field(..., ge=0, le=100, description="Eligibility score (0-100)")
    risk_level: RiskLevel = Field(..., description="Risk level classification")
    recommendation: Recommendation = Field(..., description="Recommended action")
    risk_flags: List[RiskFlag] = Field(default=[], description="Detected risk indicators")
    return_window_days: int = Field(..., description="Applicable return window")
    confidence: float = Field(..., ge=0, le=1, description="Model confidence")

    # Additional context
    buyer_return_rate: Optional[float] = Field(None, description="Buyer's historical return rate")
    days_since_order: int = Field(..., description="Days since order was placed")
    within_return_window: bool = Field(..., description="Whether request is within window")

    # For tracking
    request_id: Optional[str] = Field(None, description="ID if return request was created")


class DashboardStats(BaseModel):
    """Statistics for merchant dashboard."""
    total_returns: int
    approved_returns: int
    denied_returns: int
    pending_returns: int
    approval_rate: float
    avg_score: float
    total_buyers: int
    high_risk_buyers: int
    total_products: int
    high_return_products: int
    returns_this_week: int
    returns_last_week: int
