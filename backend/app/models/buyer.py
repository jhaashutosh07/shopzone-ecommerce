from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class Buyer(Base):
    __tablename__ = "buyers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    merchant_id = Column(String(36), ForeignKey("merchants.id"), nullable=False, index=True)
    external_buyer_id = Column(String(255), nullable=False, index=True)

    # Behavior metrics
    total_orders = Column(Integer, default=0)
    total_returns = Column(Integer, default=0)
    total_reviews = Column(Integer, default=0)
    avg_review_score = Column(Float, default=0.0)  # 1-5 scale
    total_spend = Column(Float, default=0.0)

    # Timestamps
    account_created_at = Column(DateTime, nullable=True)
    last_order_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    merchant = relationship("Merchant", back_populates="buyers")
    return_requests = relationship("ReturnRequest", back_populates="buyer", cascade="all, delete-orphan")

    @property
    def return_rate(self) -> float:
        """Calculate the buyer's return rate."""
        if self.total_orders == 0:
            return 0.0
        return self.total_returns / self.total_orders

    @property
    def account_age_days(self) -> int:
        """Calculate account age in days."""
        if not self.account_created_at:
            return 0
        return (datetime.utcnow() - self.account_created_at).days

    def __repr__(self):
        return f"<Buyer {self.external_buyer_id}>"
