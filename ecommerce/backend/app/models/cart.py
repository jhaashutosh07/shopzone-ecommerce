from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class Cart(Base):
    __tablename__ = "carts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, unique=True, index=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="cart")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")

    @property
    def total_items(self) -> int:
        return sum(item.quantity for item in self.items)

    @property
    def subtotal(self) -> float:
        return sum(item.total_price for item in self.items)

    @property
    def tax(self) -> float:
        return self.subtotal * 0.18  # 18% GST

    @property
    def total(self) -> float:
        return self.subtotal + self.tax

    def __repr__(self):
        return f"<Cart {self.user_id}>"


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cart_id = Column(String(36), ForeignKey("carts.id"), nullable=False, index=True)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)

    quantity = Column(Integer, default=1)

    # Store selected variants
    selected_size = Column(String(50), nullable=True)
    selected_color = Column(String(50), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    cart = relationship("Cart", back_populates="items")
    product = relationship("Product", back_populates="cart_items")

    @property
    def unit_price(self) -> float:
        return self.product.price if self.product else 0

    @property
    def total_price(self) -> float:
        return self.unit_price * self.quantity

    def __repr__(self):
        return f"<CartItem {self.product_id} x{self.quantity}>"
