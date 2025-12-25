from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import random
import string
import json

from app.database import get_db
from app.models.user import User
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.models.return_request import ReturnRequest, ReturnStatus, ReturnReason
from app.schemas.return_request import (
    ReturnRequestCreate, ReturnRequestResponse, ReturnRequestListResponse,
    ReturnDecisionUpdate, SchedulePickup
)
from app.services.auth import get_current_user, get_current_seller
from app.services.return_engine import return_engine_client

router = APIRouter(prefix="/returns", tags=["Returns"])


def generate_return_number() -> str:
    """Generate unique return number."""
    timestamp = datetime.utcnow().strftime("%Y%m%d")
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"RET-{timestamp}-{random_part}"


@router.post("", response_model=ReturnRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_return_request(
    return_data: ReturnRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a return request for an order item.

    This endpoint integrates with the Return Policy Engine to:
    1. Score the return request based on buyer/product data
    2. Get risk assessment and recommendation
    3. Auto-approve/deny based on merchant thresholds
    """
    # Get order
    order = db.query(Order).filter(
        Order.id == return_data.order_id,
        Order.user_id == current_user.id
    ).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status != OrderStatus.DELIVERED:
        raise HTTPException(
            status_code=400,
            detail="Can only return items from delivered orders"
        )

    # Get order item
    order_item = db.query(OrderItem).filter(
        OrderItem.id == return_data.order_item_id,
        OrderItem.order_id == order.id
    ).first()

    if not order_item:
        raise HTTPException(status_code=404, detail="Order item not found")

    if order_item.is_returned:
        raise HTTPException(status_code=400, detail="Item already returned")

    if not order_item.can_return:
        raise HTTPException(
            status_code=400,
            detail=f"Return window of {order_item.return_window_days} days has expired"
        )

    # Get product
    product = db.query(Product).filter(Product.id == order_item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if not product.is_returnable:
        raise HTTPException(status_code=400, detail="This product is not returnable")

    # Check for existing pending return
    existing = db.query(ReturnRequest).filter(
        ReturnRequest.order_item_id == order_item.id,
        ReturnRequest.status.in_([ReturnStatus.PENDING, ReturnStatus.APPROVED])
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Return request already exists for this item"
        )

    # Create return request
    return_request = ReturnRequest(
        order_id=order.id,
        order_item_id=order_item.id,
        user_id=current_user.id,
        return_number=generate_return_number(),
        reason=return_data.reason,
        reason_details=return_data.reason_details,
        images=json.dumps(return_data.images) if return_data.images else None,
        refund_amount=order_item.total_price
    )
    db.add(return_request)
    db.commit()
    db.refresh(return_request)

    # Call Return Policy Engine for scoring
    try:
        score_result = await return_engine_client.get_return_score(
            buyer=current_user,
            product=product,
            order=order,
            order_item=order_item,
            return_reason=return_data.reason.value
        )

        if score_result:
            return_request.eligibility_score = score_result.get("score")
            return_request.risk_level = score_result.get("risk_level")
            return_request.risk_flags = json.dumps(score_result.get("risk_flags", []))
            return_request.engine_recommendation = score_result.get("recommendation")
            return_request.engine_confidence = score_result.get("confidence")

            # Auto-decision based on recommendation
            recommendation = score_result.get("recommendation")
            if recommendation == "APPROVE":
                return_request.status = ReturnStatus.APPROVED
                return_request.decision = "approved"
                return_request.decided_by = "system"
                return_request.decision_notes = "Auto-approved by Return Policy Engine"
                return_request.approved_at = datetime.utcnow()
            elif recommendation == "DENY":
                return_request.status = ReturnStatus.REJECTED
                return_request.decision = "rejected"
                return_request.decided_by = "system"
                return_request.decision_notes = "Auto-denied by Return Policy Engine due to high risk"
                return_request.rejected_at = datetime.utcnow()
            # REVIEW stays as PENDING for manual review

            db.commit()
            db.refresh(return_request)

    except Exception as e:
        # Log error but don't fail the return request
        print(f"Return Policy Engine error: {e}")

    # Sync buyer data to Return Policy Engine
    await return_engine_client.sync_buyer(current_user)

    return ReturnRequestResponse(
        id=return_request.id,
        return_number=return_request.return_number,
        order_id=return_request.order_id,
        order_item_id=return_request.order_item_id,
        user_id=return_request.user_id,
        reason=return_request.reason,
        reason_details=return_request.reason_details,
        status=return_request.status,
        eligibility_score=return_request.eligibility_score,
        risk_level=return_request.risk_level,
        risk_flags=return_request.risk_flags,
        engine_recommendation=return_request.engine_recommendation,
        engine_confidence=return_request.engine_confidence,
        decision=return_request.decision,
        decided_by=return_request.decided_by,
        decision_notes=return_request.decision_notes,
        refund_amount=return_request.refund_amount,
        refund_method=return_request.refund_method,
        pickup_date=return_request.pickup_date,
        pickup_slot=return_request.pickup_slot,
        days_since_delivery=return_request.days_since_delivery,
        created_at=return_request.created_at,
        approved_at=return_request.approved_at,
        rejected_at=return_request.rejected_at,
        refunded_at=return_request.refunded_at,
        product_name=order_item.product_name,
        product_image=order_item.product_image,
        order_amount=order_item.total_price
    )


@router.get("", response_model=List[ReturnRequestListResponse])
def list_returns(
    status: ReturnStatus = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's return requests."""
    query = db.query(ReturnRequest).filter(ReturnRequest.user_id == current_user.id)

    if status:
        query = query.filter(ReturnRequest.status == status)

    returns = query.order_by(ReturnRequest.created_at.desc()).offset(
        (page - 1) * per_page
    ).limit(per_page).all()

    result = []
    for ret in returns:
        order_item = db.query(OrderItem).filter(OrderItem.id == ret.order_item_id).first()
        order = db.query(Order).filter(Order.id == ret.order_id).first()

        result.append(ReturnRequestListResponse(
            id=ret.id,
            return_number=ret.return_number,
            order_number=order.order_number if order else "",
            status=ret.status,
            reason=ret.reason,
            eligibility_score=ret.eligibility_score,
            risk_level=ret.risk_level,
            engine_recommendation=ret.engine_recommendation,
            product_name=order_item.product_name if order_item else "",
            product_image=order_item.product_image if order_item else None,
            refund_amount=ret.refund_amount,
            created_at=ret.created_at
        ))

    return result


@router.get("/{return_id}", response_model=ReturnRequestResponse)
def get_return(
    return_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get return request details."""
    return_request = db.query(ReturnRequest).filter(
        ReturnRequest.id == return_id,
        ReturnRequest.user_id == current_user.id
    ).first()

    if not return_request:
        # Try by return number
        return_request = db.query(ReturnRequest).filter(
            ReturnRequest.return_number == return_id,
            ReturnRequest.user_id == current_user.id
        ).first()

    if not return_request:
        raise HTTPException(status_code=404, detail="Return request not found")

    order_item = db.query(OrderItem).filter(
        OrderItem.id == return_request.order_item_id
    ).first()

    return ReturnRequestResponse(
        id=return_request.id,
        return_number=return_request.return_number,
        order_id=return_request.order_id,
        order_item_id=return_request.order_item_id,
        user_id=return_request.user_id,
        reason=return_request.reason,
        reason_details=return_request.reason_details,
        status=return_request.status,
        eligibility_score=return_request.eligibility_score,
        risk_level=return_request.risk_level,
        risk_flags=return_request.risk_flags,
        engine_recommendation=return_request.engine_recommendation,
        engine_confidence=return_request.engine_confidence,
        decision=return_request.decision,
        decided_by=return_request.decided_by,
        decision_notes=return_request.decision_notes,
        refund_amount=return_request.refund_amount,
        refund_method=return_request.refund_method,
        pickup_date=return_request.pickup_date,
        pickup_slot=return_request.pickup_slot,
        days_since_delivery=return_request.days_since_delivery,
        created_at=return_request.created_at,
        approved_at=return_request.approved_at,
        rejected_at=return_request.rejected_at,
        refunded_at=return_request.refunded_at,
        product_name=order_item.product_name if order_item else None,
        product_image=order_item.product_image if order_item else None,
        order_amount=order_item.total_price if order_item else None
    )


@router.post("/{return_id}/cancel", response_model=ReturnRequestResponse)
def cancel_return(
    return_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel a return request."""
    return_request = db.query(ReturnRequest).filter(
        ReturnRequest.id == return_id,
        ReturnRequest.user_id == current_user.id
    ).first()

    if not return_request:
        raise HTTPException(status_code=404, detail="Return request not found")

    if return_request.status not in [ReturnStatus.PENDING, ReturnStatus.APPROVED]:
        raise HTTPException(
            status_code=400,
            detail="Cannot cancel return at this stage"
        )

    return_request.status = ReturnStatus.CANCELLED
    db.commit()
    db.refresh(return_request)

    order_item = db.query(OrderItem).filter(
        OrderItem.id == return_request.order_item_id
    ).first()

    return ReturnRequestResponse(
        id=return_request.id,
        return_number=return_request.return_number,
        order_id=return_request.order_id,
        order_item_id=return_request.order_item_id,
        user_id=return_request.user_id,
        reason=return_request.reason,
        reason_details=return_request.reason_details,
        status=return_request.status,
        eligibility_score=return_request.eligibility_score,
        risk_level=return_request.risk_level,
        risk_flags=return_request.risk_flags,
        engine_recommendation=return_request.engine_recommendation,
        engine_confidence=return_request.engine_confidence,
        decision=return_request.decision,
        decided_by=return_request.decided_by,
        decision_notes=return_request.decision_notes,
        refund_amount=return_request.refund_amount,
        refund_method=return_request.refund_method,
        pickup_date=return_request.pickup_date,
        pickup_slot=return_request.pickup_slot,
        days_since_delivery=return_request.days_since_delivery,
        created_at=return_request.created_at,
        approved_at=return_request.approved_at,
        rejected_at=return_request.rejected_at,
        refunded_at=return_request.refunded_at,
        product_name=order_item.product_name if order_item else None,
        product_image=order_item.product_image if order_item else None,
        order_amount=order_item.total_price if order_item else None
    )


# Seller endpoints
@router.get("/seller/all", response_model=List[ReturnRequestListResponse])
def get_seller_returns(
    status: ReturnStatus = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    seller: User = Depends(get_current_seller),
    db: Session = Depends(get_db)
):
    """Get return requests for seller's products."""
    # Get seller's product IDs
    seller_product_ids = [p.id for p in seller.products]

    query = db.query(ReturnRequest).join(OrderItem).filter(
        OrderItem.product_id.in_(seller_product_ids)
    )

    if status:
        query = query.filter(ReturnRequest.status == status)

    returns = query.order_by(ReturnRequest.created_at.desc()).offset(
        (page - 1) * per_page
    ).limit(per_page).all()

    result = []
    for ret in returns:
        order_item = db.query(OrderItem).filter(OrderItem.id == ret.order_item_id).first()
        order = db.query(Order).filter(Order.id == ret.order_id).first()

        result.append(ReturnRequestListResponse(
            id=ret.id,
            return_number=ret.return_number,
            order_number=order.order_number if order else "",
            status=ret.status,
            reason=ret.reason,
            eligibility_score=ret.eligibility_score,
            risk_level=ret.risk_level,
            engine_recommendation=ret.engine_recommendation,
            product_name=order_item.product_name if order_item else "",
            product_image=order_item.product_image if order_item else None,
            refund_amount=ret.refund_amount,
            created_at=ret.created_at
        ))

    return result


@router.put("/seller/{return_id}/decision", response_model=ReturnRequestResponse)
def make_return_decision(
    return_id: str,
    decision_data: ReturnDecisionUpdate,
    seller: User = Depends(get_current_seller),
    db: Session = Depends(get_db)
):
    """Make a decision on a return request (approve/reject)."""
    return_request = db.query(ReturnRequest).filter(
        ReturnRequest.id == return_id
    ).first()

    if not return_request:
        raise HTTPException(status_code=404, detail="Return request not found")

    if return_request.status != ReturnStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail="Can only make decision on pending returns"
        )

    # Update decision
    return_request.decision = decision_data.decision
    return_request.decided_by = seller.id
    return_request.decision_notes = decision_data.decision_notes

    if decision_data.decision == "approved":
        return_request.status = ReturnStatus.APPROVED
        return_request.approved_at = datetime.utcnow()
        if decision_data.refund_amount:
            return_request.refund_amount = decision_data.refund_amount
        if decision_data.refund_method:
            return_request.refund_method = decision_data.refund_method
    else:
        return_request.status = ReturnStatus.REJECTED
        return_request.rejected_at = datetime.utcnow()

    db.commit()
    db.refresh(return_request)

    order_item = db.query(OrderItem).filter(
        OrderItem.id == return_request.order_item_id
    ).first()

    return ReturnRequestResponse(
        id=return_request.id,
        return_number=return_request.return_number,
        order_id=return_request.order_id,
        order_item_id=return_request.order_item_id,
        user_id=return_request.user_id,
        reason=return_request.reason,
        reason_details=return_request.reason_details,
        status=return_request.status,
        eligibility_score=return_request.eligibility_score,
        risk_level=return_request.risk_level,
        risk_flags=return_request.risk_flags,
        engine_recommendation=return_request.engine_recommendation,
        engine_confidence=return_request.engine_confidence,
        decision=return_request.decision,
        decided_by=return_request.decided_by,
        decision_notes=return_request.decision_notes,
        refund_amount=return_request.refund_amount,
        refund_method=return_request.refund_method,
        pickup_date=return_request.pickup_date,
        pickup_slot=return_request.pickup_slot,
        days_since_delivery=return_request.days_since_delivery,
        created_at=return_request.created_at,
        approved_at=return_request.approved_at,
        rejected_at=return_request.rejected_at,
        refunded_at=return_request.refunded_at,
        product_name=order_item.product_name if order_item else None,
        product_image=order_item.product_image if order_item else None,
        order_amount=order_item.total_price if order_item else None
    )


@router.post("/seller/{return_id}/pickup", response_model=ReturnRequestResponse)
def schedule_pickup(
    return_id: str,
    pickup_data: SchedulePickup,
    seller: User = Depends(get_current_seller),
    db: Session = Depends(get_db)
):
    """Schedule pickup for approved return."""
    return_request = db.query(ReturnRequest).filter(
        ReturnRequest.id == return_id
    ).first()

    if not return_request:
        raise HTTPException(status_code=404, detail="Return request not found")

    if return_request.status != ReturnStatus.APPROVED:
        raise HTTPException(
            status_code=400,
            detail="Can only schedule pickup for approved returns"
        )

    return_request.pickup_address = pickup_data.pickup_address
    return_request.pickup_date = pickup_data.pickup_date
    return_request.pickup_slot = pickup_data.pickup_slot
    return_request.status = ReturnStatus.PICKUP_SCHEDULED

    db.commit()
    db.refresh(return_request)

    order_item = db.query(OrderItem).filter(
        OrderItem.id == return_request.order_item_id
    ).first()

    return ReturnRequestResponse(
        id=return_request.id,
        return_number=return_request.return_number,
        order_id=return_request.order_id,
        order_item_id=return_request.order_item_id,
        user_id=return_request.user_id,
        reason=return_request.reason,
        reason_details=return_request.reason_details,
        status=return_request.status,
        eligibility_score=return_request.eligibility_score,
        risk_level=return_request.risk_level,
        risk_flags=return_request.risk_flags,
        engine_recommendation=return_request.engine_recommendation,
        engine_confidence=return_request.engine_confidence,
        decision=return_request.decision,
        decided_by=return_request.decided_by,
        decision_notes=return_request.decision_notes,
        refund_amount=return_request.refund_amount,
        refund_method=return_request.refund_method,
        pickup_date=return_request.pickup_date,
        pickup_slot=return_request.pickup_slot,
        days_since_delivery=return_request.days_since_delivery,
        created_at=return_request.created_at,
        approved_at=return_request.approved_at,
        rejected_at=return_request.rejected_at,
        refunded_at=return_request.refunded_at,
        product_name=order_item.product_name if order_item else None,
        product_image=order_item.product_image if order_item else None,
        order_amount=order_item.total_price if order_item else None
    )


@router.post("/seller/{return_id}/refund", response_model=ReturnRequestResponse)
def process_refund(
    return_id: str,
    seller: User = Depends(get_current_seller),
    db: Session = Depends(get_db)
):
    """Process refund for a return (after item received)."""
    return_request = db.query(ReturnRequest).filter(
        ReturnRequest.id == return_id
    ).first()

    if not return_request:
        raise HTTPException(status_code=404, detail="Return request not found")

    if return_request.status != ReturnStatus.RECEIVED:
        raise HTTPException(
            status_code=400,
            detail="Can only refund after item is received"
        )

    # Mark order item as returned
    order_item = db.query(OrderItem).filter(
        OrderItem.id == return_request.order_item_id
    ).first()
    if order_item:
        order_item.is_returned = True

        # Update product stats
        product = db.query(Product).filter(Product.id == order_item.product_id).first()
        if product:
            product.total_returned += order_item.quantity
            product.stock_quantity += order_item.quantity

    # Update user stats
    user = db.query(User).filter(User.id == return_request.user_id).first()
    if user:
        user.total_returns += 1

    # Process refund
    return_request.status = ReturnStatus.REFUND_COMPLETED
    return_request.refunded_at = datetime.utcnow()
    return_request.refund_id = f"REF-{return_request.return_number}"

    db.commit()
    db.refresh(return_request)

    return ReturnRequestResponse(
        id=return_request.id,
        return_number=return_request.return_number,
        order_id=return_request.order_id,
        order_item_id=return_request.order_item_id,
        user_id=return_request.user_id,
        reason=return_request.reason,
        reason_details=return_request.reason_details,
        status=return_request.status,
        eligibility_score=return_request.eligibility_score,
        risk_level=return_request.risk_level,
        risk_flags=return_request.risk_flags,
        engine_recommendation=return_request.engine_recommendation,
        engine_confidence=return_request.engine_confidence,
        decision=return_request.decision,
        decided_by=return_request.decided_by,
        decision_notes=return_request.decision_notes,
        refund_amount=return_request.refund_amount,
        refund_method=return_request.refund_method,
        pickup_date=return_request.pickup_date,
        pickup_slot=return_request.pickup_slot,
        days_since_delivery=return_request.days_since_delivery,
        created_at=return_request.created_at,
        approved_at=return_request.approved_at,
        rejected_at=return_request.rejected_at,
        refunded_at=return_request.refunded_at,
        product_name=order_item.product_name if order_item else None,
        product_image=order_item.product_image if order_item else None,
        order_amount=order_item.total_price if order_item else None
    )
