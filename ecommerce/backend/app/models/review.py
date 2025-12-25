from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False, index=True)
    order_id = Column(String(36), ForeignKey("orders.id"), nullable=True)

    # Review content
    rating = Column(Integer, nullable=False)  # 1-5
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=True)

    # Media
    images = Column(Text, nullable=True)  # JSON array of URLs

    # Verification
    is_verified_purchase = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=True)

    # Helpfulness
    helpful_count = Column(Integer, default=0)
    not_helpful_count = Column(Integer, default=0)

    # Seller response
    seller_response = Column(Text, nullable=True)
    seller_responded_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")

    def __repr__(self):
        return f"<Review {self.product_id} - {self.rating} stars>"
