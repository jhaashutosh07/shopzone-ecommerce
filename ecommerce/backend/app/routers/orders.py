from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import random
import string

from app.database import get_db
from app.models.user import User
from app.models.cart import Cart, CartItem
from app.models.order import Order, OrderItem, OrderStatus, PaymentStatus
from app.models.address import Address
from app.models.product import Product
from app.schemas.order import (
    OrderCreate, OrderResponse, OrderListResponse,
    OrderItemResponse, OrderStatusUpdate
)
from app.services.auth import get_current_user, get_current_seller

router = APIRouter(prefix="/orders", tags=["Orders"])


def generate_order_number() -> str:
    """Generate unique order number."""
    timestamp = datetime.utcnow().strftime("%Y%m%d")
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"ORD-{timestamp}-{random_part}"


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new order from cart."""
    # Get cart
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # Get address
    address = db.query(Address).filter(
        Address.id == order_data.address_id,
        Address.user_id == current_user.id
    ).first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")

    # Validate stock
    for cart_item in cart.items:
        if cart_item.quantity > cart_item.product.stock_quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for {cart_item.product.name}"
            )

    # Calculate totals
    subtotal = cart.subtotal
    tax = cart.tax
    shipping_fee = 0 if subtotal > 500 else 40  # Free shipping over 500
    total = subtotal + tax + shipping_fee

    # Create order
    order = Order(
        user_id=current_user.id,
        order_number=generate_order_number(),
        status=OrderStatus.PENDING,
        payment_status=PaymentStatus.PENDING if order_data.payment_method == "cod" else PaymentStatus.PENDING,
        subtotal=subtotal,
        tax=tax,
        shipping_fee=shipping_fee,
        discount=0,
        total=total,
        payment_method=order_data.payment_method,
        shipping_name=address.full_name,
        shipping_phone=address.phone,
        shipping_address=f"{address.address_line1}, {address.address_line2 or ''}".strip(", "),
        shipping_city=address.city,
        shipping_state=address.state,
        shipping_postal_code=address.postal_code,
        shipping_country=address.country,
        customer_notes=order_data.customer_notes
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # Create order items and update inventory
    for cart_item in cart.items:
        product = cart_item.product
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            product_name=product.name,
            product_image=product.primary_image,
            product_sku=product.sku,
            unit_price=product.price,
            quantity=cart_item.quantity,
            total_price=cart_item.total_price,
            selected_size=cart_item.selected_size,
            selected_color=cart_item.selected_color,
            return_window_days=product.return_window_days
        )
        db.add(order_item)

        # Update stock
        product.stock_quantity -= cart_item.quantity
        product.total_sold += cart_item.quantity

    # Update user stats
    current_user.total_orders += 1
    current_user.total_spend += total

    # Clear cart
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()

    # For COD, mark as confirmed
    if order_data.payment_method == "cod":
        order.status = OrderStatus.CONFIRMED
        order.confirmed_at = datetime.utcnow()

    db.commit()
    db.refresh(order)

    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
        user_id=order.user_id,
        status=order.status,
        payment_status=order.payment_status,
        subtotal=order.subtotal,
        tax=order.tax,
        shipping_fee=order.shipping_fee,
        discount=order.discount,
        total=order.total,
        payment_method=order.payment_method,
        shipping_name=order.shipping_name,
        shipping_phone=order.shipping_phone,
        shipping_address=order.shipping_address,
        shipping_city=order.shipping_city,
        shipping_state=order.shipping_state,
        shipping_postal_code=order.shipping_postal_code,
        tracking_number=order.tracking_number,
        carrier=order.carrier,
        items=[OrderItemResponse(
            id=item.id,
            product_id=item.product_id,
            product_name=item.product_name,
            product_image=item.product_image,
            product_sku=item.product_sku,
            unit_price=item.unit_price,
            quantity=item.quantity,
            total_price=item.total_price,
            selected_size=item.selected_size,
            selected_color=item.selected_color,
            return_window_days=item.return_window_days,
            is_returned=item.is_returned,
            can_return=item.can_return
        ) for item in order.items],
        item_count=order.item_count,
        can_cancel=order.can_cancel,
        can_return=order.can_return,
        created_at=order.created_at,
        confirmed_at=order.confirmed_at,
        shipped_at=order.shipped_at,
        delivered_at=order.delivered_at
    )


@router.get("", response_model=List[OrderListResponse])
def list_orders(
    status: OrderStatus = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's orders."""
    query = db.query(Order).filter(Order.user_id == current_user.id)

    if status:
        query = query.filter(Order.status == status)

    orders = query.order_by(Order.created_at.desc()).offset(
        (page - 1) * per_page
    ).limit(per_page).all()

    return [OrderListResponse(
        id=order.id,
        order_number=order.order_number,
        status=order.status,
        payment_status=order.payment_status,
        total=order.total,
        item_count=order.item_count,
        created_at=order.created_at,
        first_item_image=order.items[0].product_image if order.items else None,
        first_item_name=order.items[0].product_name if order.items else None
    ) for order in orders]


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get order details."""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()

    if not order:
        # Try by order number
        order = db.query(Order).filter(
            Order.order_number == order_id,
            Order.user_id == current_user.id
        ).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
        user_id=order.user_id,
        status=order.status,
        payment_status=order.payment_status,
        subtotal=order.subtotal,
        tax=order.tax,
        shipping_fee=order.shipping_fee,
        discount=order.discount,
        total=order.total,
        payment_method=order.payment_method,
        shipping_name=order.shipping_name,
        shipping_phone=order.shipping_phone,
        shipping_address=order.shipping_address,
        shipping_city=order.shipping_city,
        shipping_state=order.shipping_state,
        shipping_postal_code=order.shipping_postal_code,
        tracking_number=order.tracking_number,
        carrier=order.carrier,
        items=[OrderItemResponse(
            id=item.id,
            product_id=item.product_id,
            product_name=item.product_name,
            product_image=item.product_image,
            product_sku=item.product_sku,
            unit_price=item.unit_price,
            quantity=item.quantity,
            total_price=item.total_price,
            selected_size=item.selected_size,
            selected_color=item.selected_color,
            return_window_days=item.return_window_days,
            is_returned=item.is_returned,
            can_return=item.can_return
        ) for item in order.items],
        item_count=order.item_count,
        can_cancel=order.can_cancel,
        can_return=order.can_return,
        created_at=order.created_at,
        confirmed_at=order.confirmed_at,
        shipped_at=order.shipped_at,
        delivered_at=order.delivered_at
    )


@router.post("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel an order."""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if not order.can_cancel:
        raise HTTPException(
            status_code=400,
            detail="Order cannot be cancelled at this stage"
        )

    # Restore stock
    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            product.stock_quantity += item.quantity
            product.total_sold -= item.quantity

    # Update order
    order.status = OrderStatus.CANCELLED
    order.cancelled_at = datetime.utcnow()

    # Refund if paid
    if order.payment_status == PaymentStatus.PAID:
        order.payment_status = PaymentStatus.REFUNDED

    db.commit()
    db.refresh(order)

    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
        user_id=order.user_id,
        status=order.status,
        payment_status=order.payment_status,
        subtotal=order.subtotal,
        tax=order.tax,
        shipping_fee=order.shipping_fee,
        discount=order.discount,
        total=order.total,
        payment_method=order.payment_method,
        shipping_name=order.shipping_name,
        shipping_phone=order.shipping_phone,
        shipping_address=order.shipping_address,
        shipping_city=order.shipping_city,
        shipping_state=order.shipping_state,
        shipping_postal_code=order.shipping_postal_code,
        tracking_number=order.tracking_number,
        carrier=order.carrier,
        items=[OrderItemResponse(
            id=item.id,
            product_id=item.product_id,
            product_name=item.product_name,
            product_image=item.product_image,
            product_sku=item.product_sku,
            unit_price=item.unit_price,
            quantity=item.quantity,
            total_price=item.total_price,
            selected_size=item.selected_size,
            selected_color=item.selected_color,
            return_window_days=item.return_window_days,
            is_returned=item.is_returned,
            can_return=item.can_return
        ) for item in order.items],
        item_count=order.item_count,
        can_cancel=order.can_cancel,
        can_return=order.can_return,
        created_at=order.created_at,
        confirmed_at=order.confirmed_at,
        shipped_at=order.shipped_at,
        delivered_at=order.delivered_at
    )


# Seller endpoints
@router.get("/seller/all", response_model=List[OrderListResponse])
def get_seller_orders(
    status: OrderStatus = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    seller: User = Depends(get_current_seller),
    db: Session = Depends(get_db)
):
    """Get orders containing seller's products."""
    # Get orders that contain this seller's products
    seller_product_ids = [p.id for p in seller.products]

    query = db.query(Order).join(OrderItem).filter(
        OrderItem.product_id.in_(seller_product_ids)
    ).distinct()

    if status:
        query = query.filter(Order.status == status)

    orders = query.order_by(Order.created_at.desc()).offset(
        (page - 1) * per_page
    ).limit(per_page).all()

    return [OrderListResponse(
        id=order.id,
        order_number=order.order_number,
        status=order.status,
        payment_status=order.payment_status,
        total=order.total,
        item_count=order.item_count,
        created_at=order.created_at,
        first_item_image=order.items[0].product_image if order.items else None,
        first_item_name=order.items[0].product_name if order.items else None
    ) for order in orders]


@router.put("/seller/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: str,
    status_update: OrderStatusUpdate,
    seller: User = Depends(get_current_seller),
    db: Session = Depends(get_db)
):
    """Update order status (seller/admin)."""
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Update status
    order.status = status_update.status

    if status_update.tracking_number:
        order.tracking_number = status_update.tracking_number
    if status_update.carrier:
        order.carrier = status_update.carrier
    if status_update.admin_notes:
        order.admin_notes = status_update.admin_notes

    # Set timestamps
    if status_update.status == OrderStatus.SHIPPED:
        order.shipped_at = datetime.utcnow()
    elif status_update.status == OrderStatus.DELIVERED:
        order.delivered_at = datetime.utcnow()

    db.commit()
    db.refresh(order)

    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
        user_id=order.user_id,
        status=order.status,
        payment_status=order.payment_status,
        subtotal=order.subtotal,
        tax=order.tax,
        shipping_fee=order.shipping_fee,
        discount=order.discount,
        total=order.total,
        payment_method=order.payment_method,
        shipping_name=order.shipping_name,
        shipping_phone=order.shipping_phone,
        shipping_address=order.shipping_address,
        shipping_city=order.shipping_city,
        shipping_state=order.shipping_state,
        shipping_postal_code=order.shipping_postal_code,
        tracking_number=order.tracking_number,
        carrier=order.carrier,
        items=[OrderItemResponse(
            id=item.id,
            product_id=item.product_id,
            product_name=item.product_name,
            product_image=item.product_image,
            product_sku=item.product_sku,
            unit_price=item.unit_price,
            quantity=item.quantity,
            total_price=item.total_price,
            selected_size=item.selected_size,
            selected_color=item.selected_color,
            return_window_days=item.return_window_days,
            is_returned=item.is_returned,
            can_return=item.can_return
        ) for item in order.items],
        item_count=order.item_count,
        can_cancel=order.can_cancel,
        can_return=order.can_return,
        created_at=order.created_at,
        confirmed_at=order.confirmed_at,
        shipped_at=order.shipped_at,
        delivered_at=order.delivered_at
    )
