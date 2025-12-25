from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.product import Product
from app.models.wishlist import Wishlist
from app.schemas.product import ProductListResponse
from app.services.auth import get_current_user

router = APIRouter(prefix="/wishlist", tags=["Wishlist"])


@router.get("", response_model=List[ProductListResponse])
def get_wishlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's wishlist."""
    wishlist_items = db.query(Wishlist).filter(
        Wishlist.user_id == current_user.id
    ).all()

    products = []
    for item in wishlist_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product and product.is_active:
            products.append(ProductListResponse(
                id=product.id,
                name=product.name,
                slug=product.slug,
                category=product.category,
                price=product.price,
                compare_at_price=product.compare_at_price,
                discount_percentage=product.discount_percentage,
                avg_rating=product.avg_rating,
                review_count=product.review_count,
                in_stock=product.in_stock,
                primary_image=product.primary_image,
                seller_id=product.seller_id
            ))

    return products


@router.post("/{product_id}", status_code=status.HTTP_201_CREATED)
def add_to_wishlist(
    product_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add product to wishlist."""
    # Check product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check if already in wishlist
    existing = db.query(Wishlist).filter(
        Wishlist.user_id == current_user.id,
        Wishlist.product_id == product_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Product already in wishlist")

    wishlist_item = Wishlist(
        user_id=current_user.id,
        product_id=product_id
    )
    db.add(wishlist_item)
    db.commit()

    return {"message": "Added to wishlist"}


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_wishlist(
    product_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove product from wishlist."""
    wishlist_item = db.query(Wishlist).filter(
        Wishlist.user_id == current_user.id,
        Wishlist.product_id == product_id
    ).first()

    if not wishlist_item:
        raise HTTPException(status_code=404, detail="Item not in wishlist")

    db.delete(wishlist_item)
    db.commit()


@router.get("/check/{product_id}")
def check_wishlist(
    product_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if product is in wishlist."""
    exists = db.query(Wishlist).filter(
        Wishlist.user_id == current_user.id,
        Wishlist.product_id == product_id
    ).first() is not None

    return {"in_wishlist": exists}
