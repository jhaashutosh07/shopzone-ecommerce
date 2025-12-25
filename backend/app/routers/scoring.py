from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.merchant import Merchant
from app.schemas.scoring import ScoreRequest, ScoreResponse
from app.services.auth import get_merchant_from_api_key
from app.services.scoring_engine import ScoringEngine

router = APIRouter(prefix="/score", tags=["Scoring"])


@router.post("", response_model=ScoreResponse)
def calculate_score(
    request: ScoreRequest,
    merchant: Merchant = Depends(get_merchant_from_api_key),
    db: Session = Depends(get_db)
):
    """
    Calculate return eligibility score for a buyer/product combination.

    This is the main API endpoint for merchants to integrate into their
    return request flow.

    **Authentication:** Requires API key in X-API-Key header.

    **Response:**
    - `score`: 0-100 eligibility score (higher = more eligible)
    - `risk_level`: low, medium, or high
    - `recommendation`: APPROVE, REVIEW, or DENY
    - `risk_flags`: List of detected risk indicators
    - `confidence`: Model confidence in prediction

    **Recommendations:**
    - APPROVE: Auto-approve the return
    - REVIEW: Flag for manual review
    - DENY: Auto-deny the return

    Thresholds can be configured in merchant settings.
    """
    scoring_engine = ScoringEngine(db, merchant)
    return scoring_engine.calculate_score(request)
