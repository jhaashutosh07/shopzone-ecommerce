from sqlalchemy import Column, String, Boolean, DateTime, Enum, Float, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base


class UserRole(str, enum.Enum):
    BUYER = "buyer"
    SELLER = "seller"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.BUYER)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Profile
    avatar_url = Column(String(500), nullable=True)

    # Seller specific
    store_name = Column(String(255), nullable=True)
    store_description = Column(String(1000), nullable=True)

    # Stats (for buyers)
    total_orders = Column(Integer, default=0)
    total_returns = Column(Integer, default=0)
    total_reviews = Column(Integer, default=0)
    total_spend = Column(Float, default=0.0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    addresses = relationship("Address", back_populates="user", cascade="all, delete-orphan")
    cart = relationship("Cart", back_populates="user", uselist=False, cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="seller", cascade="all, delete-orphan")
    wishlist = relationship("Wishlist", back_populates="user", cascade="all, delete-orphan")

    @property
    def return_rate(self) -> float:
        if self.total_orders == 0:
            return 0.0
        return self.total_returns / self.total_orders

    @property
    def avg_review_score(self) -> float:
        if not self.reviews:
            return 0.0
        return sum(r.rating for r in self.reviews) / len(self.reviews)

    @property
    def account_age_days(self) -> int:
        return (datetime.utcnow() - self.created_at).days

    def __repr__(self):
        return f"<User {self.email}>"
