from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base


class ReturnStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PICKUP_SCHEDULED = "pickup_scheduled"
    PICKED_UP = "picked_up"
    RECEIVED = "received"
    REFUND_INITIATED = "refund_initiated"
    REFUND_COMPLETED = "refund_completed"
    CANCELLED = "cancelled"


class ReturnReason(str, enum.Enum):
    SIZE_ISSUE = "size_issue"
    DEFECTIVE = "defective"
    NOT_AS_DESCRIBED = "not_as_described"
    CHANGED_MIND = "changed_mind"
    ARRIVED_LATE = "arrived_late"
    DAMAGED_IN_SHIPPING = "damaged_in_shipping"
    WRONG_ITEM = "wrong_item"
    BETTER_PRICE_ELSEWHERE = "better_price_elsewhere"
    OTHER = "other"


class ReturnRequest(Base):
    __tablename__ = "return_requests"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = Column(String(36), ForeignKey("orders.id"), nullable=False, index=True)
    order_item_id = Column(String(36), ForeignKey("order_items.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)

    # Return details
    return_number = Column(String(20), unique=True, nullable=False, index=True)
    reason = Column(Enum(ReturnReason), nullable=False)
    reason_details = Column(Text, nullable=True)

    # Status
    status = Column(Enum(ReturnStatus), default=ReturnStatus.PENDING)

    # Return Policy Engine Integration
    eligibility_score = Column(Float, nullable=True)
    risk_level = Column(String(20), nullable=True)  # low, medium, high
    risk_flags = Column(Text, nullable=True)  # JSON string
    engine_recommendation = Column(String(20), nullable=True)  # APPROVE, REVIEW, DENY
    engine_confidence = Column(Float, nullable=True)

    # Decision
    decision = Column(String(20), nullable=True)  # approved, rejected
    decided_by = Column(String(50), nullable=True)  # system, admin_id
    decision_notes = Column(Text, nullable=True)

    # Refund
    refund_amount = Column(Float, nullable=True)
    refund_method = Column(String(50), nullable=True)  # original_payment, store_credit, bank
    refund_id = Column(String(100), nullable=True)

    # Pickup
    pickup_address = Column(Text, nullable=True)
    pickup_date = Column(DateTime, nullable=True)
    pickup_slot = Column(String(50), nullable=True)

    # Images uploaded by customer
    images = Column(Text, nullable=True)  # JSON array of URLs

    # Dates
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)
    rejected_at = Column(DateTime, nullable=True)
    picked_up_at = Column(DateTime, nullable=True)
    received_at = Column(DateTime, nullable=True)
    refunded_at = Column(DateTime, nullable=True)

    # Relationships
    order = relationship("Order", back_populates="return_requests")
    order_item = relationship("OrderItem")
    user = relationship("User")

    @property
    def days_since_delivery(self) -> int:
        if not self.order.delivered_at:
            return 0
        return (self.created_at - self.order.delivered_at).days

    def __repr__(self):
        return f"<ReturnRequest {self.return_number}>"
