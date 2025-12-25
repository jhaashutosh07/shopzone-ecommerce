from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Enum, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base


class ProductCategory(str, enum.Enum):
    CLOTHING = "clothing"
    ELECTRONICS = "electronics"
    HOME = "home"
    BEAUTY = "beauty"
    SPORTS = "sports"
    TOYS = "toys"
    BOOKS = "books"
    GROCERY = "grocery"
    JEWELRY = "jewelry"
    AUTOMOTIVE = "automotive"
    OTHER = "other"


# Subcategories mapping
SUBCATEGORIES = {
    ProductCategory.CLOTHING: [
        "mens_shirts", "mens_pants", "mens_shoes", "womens_dresses",
        "womens_tops", "womens_pants", "womens_shoes", "kids_clothing",
        "activewear", "underwear", "accessories"
    ],
    ProductCategory.ELECTRONICS: [
        "smartphones", "laptops", "tablets", "headphones", "cameras",
        "tvs", "gaming", "smart_home", "accessories"
    ],
    ProductCategory.HOME: [
        "furniture", "kitchen", "bedding", "bath", "decor",
        "storage", "lighting", "garden"
    ],
    ProductCategory.BEAUTY: [
        "skincare", "makeup", "haircare", "fragrance", "personal_care"
    ],
    ProductCategory.SPORTS: [
        "fitness", "outdoor", "team_sports", "water_sports", "cycling"
    ],
}


class Product(Base):
    __tablename__ = "products"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    seller_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)

    # Basic info
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    short_description = Column(String(500), nullable=True)

    # Categorization
    category = Column(Enum(ProductCategory), nullable=False, index=True)
    subcategory = Column(String(100), nullable=True)
    brand = Column(String(100), nullable=True)

    # Pricing
    price = Column(Float, nullable=False)
    compare_at_price = Column(Float, nullable=True)  # Original price for discounts
    cost_price = Column(Float, nullable=True)  # For seller profit calculation

    # Inventory
    sku = Column(String(100), unique=True, nullable=False)
    stock_quantity = Column(Integer, default=0)
    low_stock_threshold = Column(Integer, default=10)
    track_inventory = Column(Boolean, default=True)

    # Attributes
    weight = Column(Float, nullable=True)  # in kg
    dimensions = Column(String(100), nullable=True)  # LxWxH
    color = Column(String(50), nullable=True)
    size = Column(String(50), nullable=True)
    material = Column(String(100), nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)

    # Return policy
    return_window_days = Column(Integer, default=30)
    is_returnable = Column(Boolean, default=True)

    # Stats
    total_sold = Column(Integer, default=0)
    total_returned = Column(Integer, default=0)
    view_count = Column(Integer, default=0)

    # SEO
    meta_title = Column(String(255), nullable=True)
    meta_description = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    seller = relationship("User", back_populates="products")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    cart_items = relationship("CartItem", back_populates="product", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="product")
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")
    wishlist_items = relationship("Wishlist", back_populates="product", cascade="all, delete-orphan")

    @property
    def return_rate(self) -> float:
        if self.total_sold == 0:
            return 0.0
        return self.total_returned / self.total_sold

    @property
    def avg_rating(self) -> float:
        if not self.reviews:
            return 0.0
        return sum(r.rating for r in self.reviews) / len(self.reviews)

    @property
    def review_count(self) -> int:
        return len(self.reviews) if self.reviews else 0

    @property
    def discount_percentage(self) -> int:
        if not self.compare_at_price or self.compare_at_price <= self.price:
            return 0
        return int(((self.compare_at_price - self.price) / self.compare_at_price) * 100)

    @property
    def in_stock(self) -> bool:
        return self.stock_quantity > 0

    @property
    def primary_image(self) -> str:
        if self.images:
            primary = next((img for img in self.images if img.is_primary), None)
            return primary.url if primary else self.images[0].url
        return "/placeholder-product.jpg"

    def __repr__(self):
        return f"<Product {self.name}>"


class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    url = Column(String(500), nullable=False)
    alt_text = Column(String(255), nullable=True)
    is_primary = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    product = relationship("Product", back_populates="images")

    def __repr__(self):
        return f"<ProductImage {self.url}>"
