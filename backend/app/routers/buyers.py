from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.merchant import Merchant
from app.models.buyer import Buyer
from app.models.product import Product
from app.schemas.buyer import (
    BuyerCreate,
    BuyerUpdate,
    BuyerResponse,
    BuyerSync,
    BuyerSyncResponse,
)
from app.services.auth import get_merchant_from_api_key, get_current_merchant

router = APIRouter(prefix="/buyers", tags=["Buyers"])


@router.post("/sync", response_model=BuyerSyncResponse)
def sync_buyers(
    sync_data: BuyerSync,
    merchant: Merchant = Depends(get_merchant_from_api_key),
    db: Session = Depends(get_db)
):
    """
    Bulk sync buyer data from merchant's platform.

    Creates new buyers or updates existing ones based on external_buyer_id.
    """
    created = 0
    updated = 0
    failed = 0
    errors = []

    for buyer_data in sync_data.buyers:
        try:
            # Check if buyer exists
            existing = db.query(Buyer).filter(
                Buyer.merchant_id == merchant.id,
                Buyer.external_buyer_id == buyer_data.external_buyer_id
            ).first()

            if existing:
                # Update existing
                for key, value in buyer_data.model_dump(exclude_unset=True).items():
                    if key != "external_buyer_id":
                        setattr(existing, key, value)
                updated += 1
            else:
                # Create new
                buyer = Buyer(
                    merchant_id=merchant.id,
                    **buyer_data.model_dump()
                )
                db.add(buyer)
                created += 1

        except Exception as e:
            failed += 1
            errors.append(f"{buyer_data.external_buyer_id}: {str(e)}")

    db.commit()

    return BuyerSyncResponse(
        created=created,
        updated=updated,
        failed=failed,
        errors=errors
    )


@router.get("", response_model=List[BuyerResponse])
def list_buyers(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    min_return_rate: float = Query(None, ge=0, le=1),
    merchant: Merchant = Depends(get_current_merchant),
    db: Session = Depends(get_db)
):
    """List buyers for the merchant (dashboard)."""
    query = db.query(Buyer).filter(Buyer.merchant_id == merchant.id)

    # Can't filter by computed property directly, so we fetch and filter
    buyers = query.order_by(Buyer.created_at.desc())\
        .offset((page - 1) * per_page)\
        .limit(per_page * 2)\
        .all()

    # Filter by return rate if specified
    if min_return_rate is not None:
        buyers = [b for b in buyers if b.return_rate >= min_return_rate]
        buyers = buyers[:per_page]
    else:
        buyers = buyers[:per_page]

    return [BuyerResponse(
        id=b.id,
        merchant_id=b.merchant_id,
        external_buyer_id=b.external_buyer_id,
        total_orders=b.total_orders,
        total_returns=b.total_returns,
        total_reviews=b.total_reviews,
        avg_review_score=b.avg_review_score,
        total_spend=b.total_spend,
        account_created_at=b.account_created_at,
        last_order_at=b.last_order_at,
        created_at=b.created_at,
        return_rate=b.return_rate
    ) for b in buyers]


@router.get("/{buyer_id}", response_model=BuyerResponse)
def get_buyer(
    buyer_id: str,
    merchant: Merchant = Depends(get_current_merchant),
    db: Session = Depends(get_db)
):
    """Get a specific buyer by ID."""
    buyer = db.query(Buyer).filter(
        Buyer.id == buyer_id,
        Buyer.merchant_id == merchant.id
    ).first()

    if not buyer:
        # Try by external ID
        buyer = db.query(Buyer).filter(
            Buyer.external_buyer_id == buyer_id,
            Buyer.merchant_id == merchant.id
        ).first()

    if not buyer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Buyer not found"
        )

    return BuyerResponse(
        id=buyer.id,
        merchant_id=buyer.merchant_id,
        external_buyer_id=buyer.external_buyer_id,
        total_orders=buyer.total_orders,
        total_returns=buyer.total_returns,
        total_reviews=buyer.total_reviews,
        avg_review_score=buyer.avg_review_score,
        total_spend=buyer.total_spend,
        account_created_at=buyer.account_created_at,
        last_order_at=buyer.last_order_at,
        created_at=buyer.created_at,
        return_rate=buyer.return_rate
    )


@router.put("/{buyer_id}", response_model=BuyerResponse)
def update_buyer(
    buyer_id: str,
    update_data: BuyerUpdate,
    merchant: Merchant = Depends(get_merchant_from_api_key),
    db: Session = Depends(get_db)
):
    """Update buyer information."""
    buyer = db.query(Buyer).filter(
        Buyer.external_buyer_id == buyer_id,
        Buyer.merchant_id == merchant.id
    ).first()

    if not buyer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Buyer not found"
        )

    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(buyer, key, value)

    db.commit()
    db.refresh(buyer)

    return BuyerResponse(
        id=buyer.id,
        merchant_id=buyer.merchant_id,
        external_buyer_id=buyer.external_buyer_id,
        total_orders=buyer.total_orders,
        total_returns=buyer.total_returns,
        total_reviews=buyer.total_reviews,
        avg_review_score=buyer.avg_review_score,
        total_spend=buyer.total_spend,
        account_created_at=buyer.account_created_at,
        last_order_at=buyer.last_order_at,
        created_at=buyer.created_at,
        return_rate=buyer.return_rate
    )
