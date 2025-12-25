from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base


class ReturnReason(str, enum.Enum):
    SIZE_ISSUE = "size_issue"
    DEFECTIVE = "defective"
    NOT_AS_DESCRIBED = "not_as_described"
    CHANGED_MIND = "changed_mind"
    ARRIVED_LATE = "arrived_late"
    DAMAGED_IN_SHIPPING = "damaged_in_shipping"
    WRONG_ITEM = "wrong_item"
    OTHER = "other"


class ReturnDecision(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    REVIEW = "review"  # Needs manual review


class ReturnRequest(Base):
    __tablename__ = "return_requests"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    merchant_id = Column(String(36), ForeignKey("merchants.id"), nullable=False, index=True)
    buyer_id = Column(String(36), ForeignKey("buyers.id"), nullable=False, index=True)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False, index=True)

    # Order info
    order_id = Column(String(255), nullable=False)
    order_date = Column(DateTime, nullable=False)
    order_amount = Column(Float, nullable=False)

    # Return request info
    request_date = Column(DateTime, default=datetime.utcnow)
    reason = Column(Enum(ReturnReason), nullable=False)
    reason_details = Column(Text, nullable=True)

    # Scoring results
    eligibility_score = Column(Float, nullable=True)
    risk_level = Column(String(20), nullable=True)  # low, medium, high
    risk_flags = Column(Text, nullable=True)  # JSON array of flags
    confidence = Column(Float, nullable=True)

    # Decision
    decision = Column(Enum(ReturnDecision), default=ReturnDecision.PENDING)
    decided_at = Column(DateTime, nullable=True)
    decided_by = Column(String(50), nullable=True)  # "system" or merchant user id

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    merchant = relationship("Merchant", back_populates="return_requests")
    buyer = relationship("Buyer", back_populates="return_requests")
    product = relationship("Product", back_populates="return_requests")

    @property
    def days_since_order(self) -> int:
        """Calculate days between order and return request."""
        return (self.request_date - self.order_date).days

    def __repr__(self):
        return f"<ReturnRequest {self.id[:8]} - {self.decision.value}>"
