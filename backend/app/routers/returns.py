from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
import json

from app.database import get_db
from app.models.merchant import Merchant
from app.models.return_request import ReturnRequest, ReturnDecision
from app.schemas.return_request import (
    ReturnRequestResponse,
    ReturnRequestUpdate,
    ReturnRequestListResponse,
)
from app.services.auth import get_merchant_from_api_key, get_current_merchant

router = APIRouter(prefix="/returns", tags=["Returns"])


def _format_return_response(return_req: ReturnRequest) -> ReturnRequestResponse:
    """Format return request for response."""
    risk_flags = []
    if return_req.risk_flags:
        try:
            risk_flags = json.loads(return_req.risk_flags)
        except json.JSONDecodeError:
            pass

    return ReturnRequestResponse(
        id=return_req.id,
        merchant_id=return_req.merchant_id,
        buyer_id=return_req.buyer_id,
        product_id=return_req.product_id,
        order_id=return_req.order_id,
        order_date=return_req.order_date,
        order_amount=return_req.order_amount,
        request_date=return_req.request_date,
        reason=return_req.reason,
        reason_details=return_req.reason_details,
        eligibility_score=return_req.eligibility_score,
        risk_level=return_req.risk_level,
        risk_flags=risk_flags,
        confidence=return_req.confidence,
        decision=return_req.decision,
        decided_at=return_req.decided_at,
        decided_by=return_req.decided_by,
        days_since_order=return_req.days_since_order,
        created_at=return_req.created_at,
    )


@router.get("/{return_id}", response_model=ReturnRequestResponse)
def get_return_request(
    return_id: str,
    merchant: Merchant = Depends(get_merchant_from_api_key),
    db: Session = Depends(get_db)
):
    """Get a specific return request by ID."""
    return_req = db.query(ReturnRequest).filter(
        ReturnRequest.id == return_id,
        ReturnRequest.merchant_id == merchant.id
    ).first()

    if not return_req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Return request not found"
        )

    return _format_return_response(return_req)


@router.get("", response_model=ReturnRequestListResponse)
def list_return_requests(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    decision: Optional[ReturnDecision] = None,
    risk_level: Optional[str] = None,
    merchant: Merchant = Depends(get_current_merchant),
    db: Session = Depends(get_db)
):
    """List return requests for the merchant (dashboard)."""
    query = db.query(ReturnRequest).filter(
        ReturnRequest.merchant_id == merchant.id
    )

    if decision:
        query = query.filter(ReturnRequest.decision == decision)
    if risk_level:
        query = query.filter(ReturnRequest.risk_level == risk_level)

    total = query.count()
    items = query.order_by(ReturnRequest.created_at.desc())\
        .offset((page - 1) * per_page)\
        .limit(per_page)\
        .all()

    return ReturnRequestListResponse(
        items=[_format_return_response(r) for r in items],
        total=total,
        page=page,
        per_page=per_page
    )


@router.put("/{return_id}", response_model=ReturnRequestResponse)
def update_return_decision(
    return_id: str,
    update_data: ReturnRequestUpdate,
    merchant: Merchant = Depends(get_current_merchant),
    db: Session = Depends(get_db)
):
    """Update the decision for a return request (manual override)."""
    return_req = db.query(ReturnRequest).filter(
        ReturnRequest.id == return_id,
        ReturnRequest.merchant_id == merchant.id
    ).first()

    if not return_req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Return request not found"
        )

    from datetime import datetime
    return_req.decision = update_data.decision
    return_req.decided_at = datetime.utcnow()
    return_req.decided_by = update_data.decided_by or merchant.id

    db.commit()
    db.refresh(return_req)

    return _format_return_response(return_req)
