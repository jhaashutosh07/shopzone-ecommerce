from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.merchant import Merchant
from app.models.product import Product
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductSync,
    ProductSyncResponse,
)
from app.services.auth import get_merchant_from_api_key, get_current_merchant

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/sync", response_model=ProductSyncResponse)
def sync_products(
    sync_data: ProductSync,
    merchant: Merchant = Depends(get_merchant_from_api_key),
    db: Session = Depends(get_db)
):
    """
    Bulk sync product data from merchant's platform.

    Creates new products or updates existing ones based on external_product_id.
    """
    created = 0
    updated = 0
    failed = 0
    errors = []

    for product_data in sync_data.products:
        try:
            # Check if product exists
            existing = db.query(Product).filter(
                Product.merchant_id == merchant.id,
                Product.external_product_id == product_data.external_product_id
            ).first()

            # Auto-calculate price tier if not provided
            if product_data.price_tier is None:
                product_data.price_tier = Product.calculate_price_tier(product_data.price)

            if existing:
                # Update existing
                for key, value in product_data.model_dump(exclude_unset=True).items():
                    if key != "external_product_id":
                        setattr(existing, key, value)
                updated += 1
            else:
                # Create new
                product = Product(
                    merchant_id=merchant.id,
                    **product_data.model_dump()
                )
                db.add(product)
                created += 1

        except Exception as e:
            failed += 1
            errors.append(f"{product_data.external_product_id}: {str(e)}")

    db.commit()

    return ProductSyncResponse(
        created=created,
        updated=updated,
        failed=failed,
        errors=errors
    )


@router.get("", response_model=List[ProductResponse])
def list_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category: str = None,
    merchant: Merchant = Depends(get_current_merchant),
    db: Session = Depends(get_db)
):
    """List products for the merchant (dashboard)."""
    query = db.query(Product).filter(Product.merchant_id == merchant.id)

    if category:
        query = query.filter(Product.category == category)

    products = query.order_by(Product.created_at.desc())\
        .offset((page - 1) * per_page)\
        .limit(per_page)\
        .all()

    return [ProductResponse(
        id=p.id,
        merchant_id=p.merchant_id,
        external_product_id=p.external_product_id,
        name=p.name,
        category=p.category,
        price=p.price,
        price_tier=p.price_tier,
        custom_return_window=p.custom_return_window,
        total_sold=p.total_sold,
        total_returned=p.total_returned,
        return_rate=p.return_rate,
        created_at=p.created_at
    ) for p in products]


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: str,
    merchant: Merchant = Depends(get_current_merchant),
    db: Session = Depends(get_db)
):
    """Get a specific product by ID."""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.merchant_id == merchant.id
    ).first()

    if not product:
        # Try by external ID
        product = db.query(Product).filter(
            Product.external_product_id == product_id,
            Product.merchant_id == merchant.id
        ).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return ProductResponse(
        id=product.id,
        merchant_id=product.merchant_id,
        external_product_id=product.external_product_id,
        name=product.name,
        category=product.category,
        price=product.price,
        price_tier=product.price_tier,
        custom_return_window=product.custom_return_window,
        total_sold=product.total_sold,
        total_returned=product.total_returned,
        return_rate=product.return_rate,
        created_at=product.created_at
    )


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: str,
    update_data: ProductUpdate,
    merchant: Merchant = Depends(get_merchant_from_api_key),
    db: Session = Depends(get_db)
):
    """Update product information."""
    product = db.query(Product).filter(
        Product.external_product_id == product_id,
        Product.merchant_id == merchant.id
    ).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(product, key, value)

    # Recalculate price tier if price changed
    if update_data.price is not None:
        product.price_tier = Product.calculate_price_tier(update_data.price)

    db.commit()
    db.refresh(product)

    return ProductResponse(
        id=product.id,
        merchant_id=product.merchant_id,
        external_product_id=product.external_product_id,
        name=product.name,
        category=product.category,
        price=product.price,
        price_tier=product.price_tier,
        custom_return_window=product.custom_return_window,
        total_sold=product.total_sold,
        total_returned=product.total_returned,
        return_rate=product.return_rate,
        created_at=product.created_at
    )
