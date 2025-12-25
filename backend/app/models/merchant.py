from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    api_key_hash = Column(String(255), unique=True, nullable=True, index=True)

    # Settings
    default_return_window = Column(Integer, default=30)  # days
    fraud_threshold = Column(Float, default=30.0)  # score below this = deny
    auto_approve_threshold = Column(Float, default=70.0)  # score above this = auto approve

    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    buyers = relationship("Buyer", back_populates="merchant", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="merchant", cascade="all, delete-orphan")
    return_requests = relationship("ReturnRequest", back_populates="merchant", cascade="all, delete-orphan")
    scoring_models = relationship("ScoringModel", back_populates="merchant", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Merchant {self.name}>"
