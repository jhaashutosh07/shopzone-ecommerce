from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.database import get_db
from app.models.merchant import Merchant
from app.models.buyer import Buyer
from app.models.product import Product
from app.models.return_request import ReturnRequest, ReturnDecision
from app.schemas.scoring import DashboardStats
from app.services.auth import get_current_merchant

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    merchant: Merchant = Depends(get_current_merchant),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics for the merchant."""
    # Return request stats
    total_returns = db.query(ReturnRequest).filter(
        ReturnRequest.merchant_id == merchant.id
    ).count()

    approved_returns = db.query(ReturnRequest).filter(
        ReturnRequest.merchant_id == merchant.id,
        ReturnRequest.decision == ReturnDecision.APPROVED
    ).count()

    denied_returns = db.query(ReturnRequest).filter(
        ReturnRequest.merchant_id == merchant.id,
        ReturnRequest.decision == ReturnDecision.DENIED
    ).count()

    pending_returns = db.query(ReturnRequest).filter(
        ReturnRequest.merchant_id == merchant.id,
        ReturnRequest.decision.in_([ReturnDecision.PENDING, ReturnDecision.REVIEW])
    ).count()

    # Approval rate
    decided_returns = approved_returns + denied_returns
    approval_rate = (approved_returns / decided_returns * 100) if decided_returns > 0 else 0

    # Average score
    avg_score_result = db.query(func.avg(ReturnRequest.eligibility_score)).filter(
        ReturnRequest.merchant_id == merchant.id,
        ReturnRequest.eligibility_score.isnot(None)
    ).scalar()
    avg_score = float(avg_score_result) if avg_score_result else 0

    # Buyer stats
    total_buyers = db.query(Buyer).filter(Buyer.merchant_id == merchant.id).count()

    # High risk buyers (return rate > 30%)
    all_buyers = db.query(Buyer).filter(Buyer.merchant_id == merchant.id).all()
    high_risk_buyers = len([b for b in all_buyers if b.return_rate > 0.3])

    # Product stats
    total_products = db.query(Product).filter(Product.merchant_id == merchant.id).count()

    all_products = db.query(Product).filter(Product.merchant_id == merchant.id).all()
    high_return_products = len([p for p in all_products if p.return_rate > 0.2])

    # Weekly returns comparison
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    two_weeks_ago = now - timedelta(days=14)

    returns_this_week = db.query(ReturnRequest).filter(
        ReturnRequest.merchant_id == merchant.id,
        ReturnRequest.created_at >= week_ago
    ).count()

    returns_last_week = db.query(ReturnRequest).filter(
        ReturnRequest.merchant_id == merchant.id,
        ReturnRequest.created_at >= two_weeks_ago,
        ReturnRequest.created_at < week_ago
    ).count()

    return DashboardStats(
        total_returns=total_returns,
        approved_returns=approved_returns,
        denied_returns=denied_returns,
        pending_returns=pending_returns,
        approval_rate=round(approval_rate, 1),
        avg_score=round(avg_score, 1),
        total_buyers=total_buyers,
        high_risk_buyers=high_risk_buyers,
        total_products=total_products,
        high_return_products=high_return_products,
        returns_this_week=returns_this_week,
        returns_last_week=returns_last_week,
    )
