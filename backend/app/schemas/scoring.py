from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

from app.models.return_request import ReturnReason

# model_version / model_type field names collide with pydantic's protected
# "model_" namespace; this config opts affected schemas out of the check.
_ALLOW_MODEL_FIELDS = ConfigDict(protected_namespaces=())


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


class FeatureContribution(BaseModel):
    """A single feature's contribution to the decision, in score points."""
    feature: str
    label: str
    value: str
    contribution: float  # positive = raised score, negative = lowered it
    direction: str  # "positive" | "negative"


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
    model_config = _ALLOW_MODEL_FIELDS
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

    # Explainability
    explanation: List[FeatureContribution] = Field(
        default=[], description="Top feature contributions behind this score"
    )
    model_version: Optional[int] = Field(None, description="Scoring model version used")

    # For tracking
    request_id: Optional[str] = Field(None, description="ID if return request was created")


class ModelVersionInfo(BaseModel):
    """A model version in the registry."""
    model_config = _ALLOW_MODEL_FIELDS
    id: str
    version: int
    model_type: str
    is_active: bool
    training_samples: int
    feedback_samples: int = 0
    accuracy: Optional[float] = None
    precision_score: Optional[float] = None
    recall_score: Optional[float] = None
    f1_score: Optional[float] = None
    roc_auc: Optional[float] = None
    trained_at: Optional[datetime] = None
    created_at: datetime


class RetrainResponse(BaseModel):
    """Result of a retraining run."""
    version: int
    metrics: dict
    feedback_samples: int
    activated: bool
    message: str


class FeatureDrift(BaseModel):
    """Drift status of one feature."""
    feature: str
    label: str
    psi: float
    status: str  # stable | moderate | drifted


class DriftReport(BaseModel):
    """Population stability of live traffic vs. the training distribution."""
    model_config = _ALLOW_MODEL_FIELDS
    model_version: Optional[int]
    samples_analyzed: int
    features: List[FeatureDrift]
    overall_status: str  # stable | moderate | drifted | insufficient_data


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
