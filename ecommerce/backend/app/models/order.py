from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Enum, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RETURNED = "returned"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class Order(Base):
    __tablename__ = "orders"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    order_number = Column(String(20), unique=True, nullable=False, index=True)

    # Status
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)

    # Pricing
    subtotal = Column(Float, nullable=False)
    tax = Column(Float, nullable=False)
    shipping_fee = Column(Float, default=0.0)
    discount = Column(Float, default=0.0)
    total = Column(Float, nullable=False)

    # Payment
    payment_method = Column(String(50), nullable=True)  # cod, card, upi, netbanking
    payment_id = Column(String(100), nullable=True)

    # Shipping address (stored as snapshot)
    shipping_name = Column(String(255), nullable=False)
    shipping_phone = Column(String(20), nullable=False)
    shipping_address = Column(Text, nullable=False)
    shipping_city = Column(String(100), nullable=False)
    shipping_state = Column(String(100), nullable=False)
    shipping_postal_code = Column(String(20), nullable=False)
    shipping_country = Column(String(100), default="India")

    # Tracking
    tracking_number = Column(String(100), nullable=True)
    carrier = Column(String(100), nullable=True)

    # Notes
    customer_notes = Column(Text, nullable=True)
    admin_notes = Column(Text, nullable=True)

    # Dates
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    confirmed_at = Column(DateTime, nullable=True)
    shipped_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    return_requests = relationship("ReturnRequest", back_populates="order", cascade="all, delete-orphan")

    @property
    def item_count(self) -> int:
        return sum(item.quantity for item in self.items)

    @property
    def can_cancel(self) -> bool:
        return self.status in [OrderStatus.PENDING, OrderStatus.CONFIRMED]

    @property
    def can_return(self) -> bool:
        return self.status == OrderStatus.DELIVERED

    def __repr__(self):
        return f"<Order {self.order_number}>"


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = Column(String(36), ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)

    # Snapshot of product at time of order
    product_name = Column(String(255), nullable=False)
    product_image = Column(String(500), nullable=True)
    product_sku = Column(String(100), nullable=False)

    # Pricing
    unit_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)

    # Variants
    selected_size = Column(String(50), nullable=True)
    selected_color = Column(String(50), nullable=True)

    # Return tracking
    return_window_days = Column(Integer, default=30)
    is_returned = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

    @property
    def can_return(self) -> bool:
        if self.is_returned:
            return False
        if not self.order.delivered_at:
            return False
        days_since_delivery = (datetime.utcnow() - self.order.delivered_at).days
        return days_since_delivery <= self.return_window_days

    def __repr__(self):
        return f"<OrderItem {self.product_name} x{self.quantity}>"


from sqlalchemy import Boolean
