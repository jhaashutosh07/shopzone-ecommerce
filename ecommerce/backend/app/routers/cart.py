from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartItemResponse, CartResponse
from app.services.auth import get_current_user

router = APIRouter(prefix="/cart", tags=["Cart"])


def get_or_create_cart(user: User, db: Session) -> Cart:
    """Get existing cart or create new one."""
    cart = db.query(Cart).filter(Cart.user_id == user.id).first()
    if not cart:
        cart = Cart(user_id=user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


@router.get("", response_model=CartResponse)
def get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's cart."""
    cart = get_or_create_cart(current_user, db)

    items = []
    for item in cart.items:
        if item.product:
            items.append(CartItemResponse(
                id=item.id,
                product_id=item.product_id,
                quantity=item.quantity,
                selected_size=item.selected_size,
                selected_color=item.selected_color,
                unit_price=item.unit_price,
                total_price=item.total_price,
                product_name=item.product.name,
                product_image=item.product.primary_image,
                product_in_stock=item.product.in_stock,
                product_stock_quantity=item.product.stock_quantity
            ))

    return CartResponse(
        id=cart.id,
        items=items,
        total_items=cart.total_items,
        subtotal=cart.subtotal,
        tax=cart.tax,
        total=cart.total
    )


@router.post("/items", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
def add_to_cart(
    item_data: CartItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add item to cart."""
    # Get product
    product = db.query(Product).filter(Product.id == item_data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if not product.is_active:
        raise HTTPException(status_code=400, detail="Product is not available")

    if not product.in_stock:
        raise HTTPException(status_code=400, detail="Product is out of stock")

    if item_data.quantity > product.stock_quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Only {product.stock_quantity} items available"
        )

    # Get or create cart
    cart = get_or_create_cart(current_user, db)

    # Check if item already in cart
    existing_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == item_data.product_id,
        CartItem.selected_size == item_data.selected_size,
        CartItem.selected_color == item_data.selected_color
    ).first()

    if existing_item:
        # Update quantity
        new_quantity = existing_item.quantity + item_data.quantity
        if new_quantity > product.stock_quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Only {product.stock_quantity} items available"
            )
        existing_item.quantity = new_quantity
    else:
        # Add new item
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            selected_size=item_data.selected_size,
            selected_color=item_data.selected_color
        )
        db.add(cart_item)

    db.commit()
    db.refresh(cart)

    # Return updated cart
    items = []
    for item in cart.items:
        if item.product:
            items.append(CartItemResponse(
                id=item.id,
                product_id=item.product_id,
                quantity=item.quantity,
                selected_size=item.selected_size,
                selected_color=item.selected_color,
                unit_price=item.unit_price,
                total_price=item.total_price,
                product_name=item.product.name,
                product_image=item.product.primary_image,
                product_in_stock=item.product.in_stock,
                product_stock_quantity=item.product.stock_quantity
            ))

    return CartResponse(
        id=cart.id,
        items=items,
        total_items=cart.total_items,
        subtotal=cart.subtotal,
        tax=cart.tax,
        total=cart.total
    )


@router.put("/items/{item_id}", response_model=CartResponse)
def update_cart_item(
    item_id: str,
    update_data: CartItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update cart item quantity."""
    cart = get_or_create_cart(current_user, db)

    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart.id
    ).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    if update_data.quantity > cart_item.product.stock_quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Only {cart_item.product.stock_quantity} items available"
        )

    cart_item.quantity = update_data.quantity
    db.commit()
    db.refresh(cart)

    # Return updated cart
    items = []
    for item in cart.items:
        if item.product:
            items.append(CartItemResponse(
                id=item.id,
                product_id=item.product_id,
                quantity=item.quantity,
                selected_size=item.selected_size,
                selected_color=item.selected_color,
                unit_price=item.unit_price,
                total_price=item.total_price,
                product_name=item.product.name,
                product_image=item.product.primary_image,
                product_in_stock=item.product.in_stock,
                product_stock_quantity=item.product.stock_quantity
            ))

    return CartResponse(
        id=cart.id,
        items=items,
        total_items=cart.total_items,
        subtotal=cart.subtotal,
        tax=cart.tax,
        total=cart.total
    )


@router.delete("/items/{item_id}", response_model=CartResponse)
def remove_cart_item(
    item_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove item from cart."""
    cart = get_or_create_cart(current_user, db)

    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart.id
    ).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    db.delete(cart_item)
    db.commit()
    db.refresh(cart)

    # Return updated cart
    items = []
    for item in cart.items:
        if item.product:
            items.append(CartItemResponse(
                id=item.id,
                product_id=item.product_id,
                quantity=item.quantity,
                selected_size=item.selected_size,
                selected_color=item.selected_color,
                unit_price=item.unit_price,
                total_price=item.total_price,
                product_name=item.product.name,
                product_image=item.product.primary_image,
                product_in_stock=item.product.in_stock,
                product_stock_quantity=item.product.stock_quantity
            ))

    return CartResponse(
        id=cart.id,
        items=items,
        total_items=cart.total_items,
        subtotal=cart.subtotal,
        tax=cart.tax,
        total=cart.total
    )


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clear all items from cart."""
    cart = get_or_create_cart(current_user, db)

    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()
