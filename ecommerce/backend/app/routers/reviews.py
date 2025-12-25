from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import json

from app.database import get_db
from app.models.user import User
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.models.review import Review
from app.schemas.review import (
    ReviewCreate, ReviewUpdate, ReviewResponse, ReviewSummary, SellerResponseCreate
)
from app.services.auth import get_current_user, get_current_seller

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a product review."""
    # Check if product exists
    product = db.query(Product).filter(Product.id == review_data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check for existing review
    existing = db.query(Review).filter(
        Review.user_id == current_user.id,
        Review.product_id == review_data.product_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="You have already reviewed this product"
        )

    # Check if verified purchase
    is_verified = False
    if review_data.order_id:
        order = db.query(Order).filter(
            Order.id == review_data.order_id,
            Order.user_id == current_user.id
        ).first()
        if order:
            order_item = db.query(OrderItem).filter(
                OrderItem.order_id == order.id,
                OrderItem.product_id == review_data.product_id
            ).first()
            if order_item:
                is_verified = True

    # Create review
    review = Review(
        user_id=current_user.id,
        product_id=review_data.product_id,
        order_id=review_data.order_id,
        rating=review_data.rating,
        title=review_data.title,
        content=review_data.content,
        images=json.dumps(review_data.images) if review_data.images else None,
        is_verified_purchase=is_verified
    )
    db.add(review)

    # Update user review count
    current_user.total_reviews += 1

    db.commit()
    db.refresh(review)

    return ReviewResponse(
        id=review.id,
        user_id=review.user_id,
        product_id=review.product_id,
        rating=review.rating,
        title=review.title,
        content=review.content,
        images=review.images,
        is_verified_purchase=review.is_verified_purchase,
        helpful_count=review.helpful_count,
        not_helpful_count=review.not_helpful_count,
        seller_response=review.seller_response,
        seller_responded_at=review.seller_responded_at,
        created_at=review.created_at,
        user_name=current_user.full_name,
        user_avatar=current_user.avatar_url
    )


@router.get("/product/{product_id}", response_model=List[ReviewResponse])
def get_product_reviews(
    product_id: str,
    sort_by: str = "recent",  # recent, helpful, rating_high, rating_low
    rating_filter: int = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get reviews for a product."""
    query = db.query(Review).filter(
        Review.product_id == product_id,
        Review.is_approved == True
    )

    if rating_filter:
        query = query.filter(Review.rating == rating_filter)

    # Sorting
    if sort_by == "helpful":
        query = query.order_by(Review.helpful_count.desc())
    elif sort_by == "rating_high":
        query = query.order_by(Review.rating.desc())
    elif sort_by == "rating_low":
        query = query.order_by(Review.rating.asc())
    else:  # recent
        query = query.order_by(Review.created_at.desc())

    reviews = query.offset((page - 1) * per_page).limit(per_page).all()

    result = []
    for review in reviews:
        user = db.query(User).filter(User.id == review.user_id).first()
        result.append(ReviewResponse(
            id=review.id,
            user_id=review.user_id,
            product_id=review.product_id,
            rating=review.rating,
            title=review.title,
            content=review.content,
            images=review.images,
            is_verified_purchase=review.is_verified_purchase,
            helpful_count=review.helpful_count,
            not_helpful_count=review.not_helpful_count,
            seller_response=review.seller_response,
            seller_responded_at=review.seller_responded_at,
            created_at=review.created_at,
            user_name=user.full_name if user else "Anonymous",
            user_avatar=user.avatar_url if user else None
        ))

    return result


@router.get("/product/{product_id}/summary", response_model=ReviewSummary)
def get_review_summary(product_id: str, db: Session = Depends(get_db)):
    """Get review summary for a product."""
    reviews = db.query(Review).filter(
        Review.product_id == product_id,
        Review.is_approved == True
    ).all()

    if not reviews:
        return ReviewSummary(
            avg_rating=0.0,
            total_reviews=0,
            rating_distribution={5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
        )

    total = len(reviews)
    avg = sum(r.rating for r in reviews) / total

    distribution = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    for review in reviews:
        distribution[review.rating] += 1

    return ReviewSummary(
        avg_rating=round(avg, 1),
        total_reviews=total,
        rating_distribution=distribution
    )


@router.put("/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: str,
    update_data: ReviewUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a review."""
    review = db.query(Review).filter(
        Review.id == review_id,
        Review.user_id == current_user.id
    ).first()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(review, key, value)

    db.commit()
    db.refresh(review)

    return ReviewResponse(
        id=review.id,
        user_id=review.user_id,
        product_id=review.product_id,
        rating=review.rating,
        title=review.title,
        content=review.content,
        images=review.images,
        is_verified_purchase=review.is_verified_purchase,
        helpful_count=review.helpful_count,
        not_helpful_count=review.not_helpful_count,
        seller_response=review.seller_response,
        seller_responded_at=review.seller_responded_at,
        created_at=review.created_at,
        user_name=current_user.full_name,
        user_avatar=current_user.avatar_url
    )


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a review."""
    review = db.query(Review).filter(
        Review.id == review_id,
        Review.user_id == current_user.id
    ).first()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    current_user.total_reviews -= 1
    db.delete(review)
    db.commit()


@router.post("/{review_id}/helpful")
def mark_helpful(
    review_id: str,
    helpful: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a review as helpful or not helpful."""
    review = db.query(Review).filter(Review.id == review_id).first()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if helpful:
        review.helpful_count += 1
    else:
        review.not_helpful_count += 1

    db.commit()
    return {"message": "Feedback recorded"}


# Seller endpoints
@router.post("/seller/{review_id}/respond", response_model=ReviewResponse)
def respond_to_review(
    review_id: str,
    response_data: SellerResponseCreate,
    seller: User = Depends(get_current_seller),
    db: Session = Depends(get_db)
):
    """Respond to a review (seller only)."""
    review = db.query(Review).filter(Review.id == review_id).first()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    # Verify seller owns the product
    product = db.query(Product).filter(
        Product.id == review.product_id,
        Product.seller_id == seller.id
    ).first()

    if not product:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to respond to this review"
        )

    review.seller_response = response_data.response
    review.seller_responded_at = datetime.utcnow()

    db.commit()
    db.refresh(review)

    user = db.query(User).filter(User.id == review.user_id).first()

    return ReviewResponse(
        id=review.id,
        user_id=review.user_id,
        product_id=review.product_id,
        rating=review.rating,
        title=review.title,
        content=review.content,
        images=review.images,
        is_verified_purchase=review.is_verified_purchase,
        helpful_count=review.helpful_count,
        not_helpful_count=review.not_helpful_count,
        seller_response=review.seller_response,
        seller_responded_at=review.seller_responded_at,
        created_at=review.created_at,
        user_name=user.full_name if user else "Anonymous",
        user_avatar=user.avatar_url if user else None
    )
