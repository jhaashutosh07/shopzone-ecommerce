from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base


class PriceTier(str, enum.Enum):
    LOW = "low"  # < $50
    MEDIUM = "medium"  # $50-200
    HIGH = "high"  # $200-500
    PREMIUM = "premium"  # > $500


class ProductCategory(str, enum.Enum):
    CLOTHING = "clothing"
    ELECTRONICS = "electronics"
    HOME = "home"
    BEAUTY = "beauty"
    SPORTS = "sports"
    TOYS = "toys"
    FOOD = "food"
    OTHER = "other"


# Category risk scores (higher = more likely to have legitimate returns)
CATEGORY_RISK_SCORES = {
    ProductCategory.CLOTHING: 0.7,  # High return rate, often size issues
    ProductCategory.ELECTRONICS: 0.5,
    ProductCategory.HOME: 0.4,
    ProductCategory.BEAUTY: 0.6,
    ProductCategory.SPORTS: 0.5,
    ProductCategory.TOYS: 0.3,
    ProductCategory.FOOD: 0.2,
    ProductCategory.OTHER: 0.5,
}


class Product(Base):
    __tablename__ = "products"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    merchant_id = Column(String(36), ForeignKey("merchants.id"), nullable=False, index=True)
    external_product_id = Column(String(255), nullable=False, index=True)

    name = Column(String(255), nullable=False)
    category = Column(Enum(ProductCategory), default=ProductCategory.OTHER)
    price = Column(Float, nullable=False)
    price_tier = Column(Enum(PriceTier), default=PriceTier.MEDIUM)

    # Custom return window (overrides merchant default)
    custom_return_window = Column(Integer, nullable=True)

    # Stats
    total_sold = Column(Integer, default=0)
    total_returned = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    merchant = relationship("Merchant", back_populates="products")
    return_requests = relationship("ReturnRequest", back_populates="product", cascade="all, delete-orphan")

    @property
    def return_rate(self) -> float:
        """Calculate the product's return rate."""
        if self.total_sold == 0:
            return 0.0
        return self.total_returned / self.total_sold

    @property
    def category_risk_score(self) -> float:
        """Get the risk score for this product's category."""
        return CATEGORY_RISK_SCORES.get(self.category, 0.5)

    @staticmethod
    def calculate_price_tier(price: float) -> PriceTier:
        """Determine price tier based on price."""
        if price < 50:
            return PriceTier.LOW
        elif price < 200:
            return PriceTier.MEDIUM
        elif price < 500:
            return PriceTier.HIGH
        else:
            return PriceTier.PREMIUM

    def __repr__(self):
        return f"<Product {self.name}>"
