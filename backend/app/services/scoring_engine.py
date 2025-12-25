from typing import Optional, List, Tuple
from datetime import datetime
import json

from sqlalchemy.orm import Session

from app.models.merchant import Merchant
from app.models.buyer import Buyer
from app.models.product import Product, CATEGORY_RISK_SCORES
from app.models.return_request import ReturnRequest, ReturnReason, ReturnDecision
from app.schemas.scoring import (
    ScoreRequest,
    ScoreResponse,
    RiskLevel,
    Recommendation,
    RiskFlag,
)
from app.config import get_settings
from app.ml.predict import MLPredictor

settings = get_settings()


class ScoringEngine:
    """Engine for calculating return eligibility scores."""

    def __init__(self, db: Session, merchant: Merchant):
        self.db = db
        self.merchant = merchant
        self.ml_predictor = MLPredictor()

    def calculate_score(self, request: ScoreRequest) -> ScoreResponse:
        """Calculate the return eligibility score."""
        # Get buyer and product from database
        buyer = self._get_or_create_buyer(request.buyer_id)
        product = self._get_or_create_product(request.product_id)

        # Calculate days since order
        days_since_order = (datetime.utcnow() - request.order_date).days

        # Determine return window
        return_window = product.custom_return_window or self.merchant.default_return_window
        within_window = days_since_order <= return_window

        # Extract features for ML model
        features = self._extract_features(buyer, product, request, days_since_order)

        # Get ML prediction
        ml_score, confidence = self.ml_predictor.predict(features)

        # Detect risk flags
        risk_flags = self._detect_risk_flags(buyer, product, request, days_since_order)

        # Adjust score based on risk flags
        adjusted_score = self._adjust_score(ml_score, risk_flags, within_window)

        # Determine risk level and recommendation
        risk_level = self._get_risk_level(adjusted_score)
        recommendation = self._get_recommendation(adjusted_score, risk_flags)

        # Create return request record
        return_request = self._create_return_request(
            buyer, product, request, adjusted_score, risk_level, risk_flags, confidence, recommendation
        )

        return ScoreResponse(
            score=round(adjusted_score, 2),
            risk_level=risk_level,
            recommendation=recommendation,
            risk_flags=risk_flags,
            return_window_days=return_window,
            confidence=round(confidence, 2),
            buyer_return_rate=round(buyer.return_rate * 100, 2),
            days_since_order=days_since_order,
            within_return_window=within_window,
            request_id=return_request.id,
        )

    def _get_or_create_buyer(self, external_buyer_id: str) -> Buyer:
        """Get or create a buyer record."""
        buyer = self.db.query(Buyer).filter(
            Buyer.merchant_id == self.merchant.id,
            Buyer.external_buyer_id == external_buyer_id
        ).first()

        if not buyer:
            buyer = Buyer(
                merchant_id=self.merchant.id,
                external_buyer_id=external_buyer_id,
            )
            self.db.add(buyer)
            self.db.commit()
            self.db.refresh(buyer)

        return buyer

    def _get_or_create_product(self, external_product_id: str) -> Product:
        """Get or create a product record."""
        product = self.db.query(Product).filter(
            Product.merchant_id == self.merchant.id,
            Product.external_product_id == external_product_id
        ).first()

        if not product:
            from app.models.product import PriceTier, ProductCategory
            product = Product(
                merchant_id=self.merchant.id,
                external_product_id=external_product_id,
                name=f"Product {external_product_id}",
                price=0.0,  # Unknown, will use default tier
                price_tier=PriceTier.MEDIUM,
                category=ProductCategory.OTHER,
            )
            self.db.add(product)
            self.db.commit()
            self.db.refresh(product)

        return product

    def _extract_features(
        self,
        buyer: Buyer,
        product: Product,
        request: ScoreRequest,
        days_since_order: int
    ) -> dict:
        """Extract features for ML model."""
        return {
            # Buyer features
            "buyer_return_rate": buyer.return_rate,
            "buyer_total_orders": buyer.total_orders,
            "buyer_total_returns": buyer.total_returns,
            "buyer_avg_review_score": buyer.avg_review_score,
            "buyer_account_age_days": buyer.account_age_days,
            "buyer_total_spend": buyer.total_spend,

            # Product features
            "product_return_rate": product.return_rate,
            "product_category_risk": product.category_risk_score,
            "product_price": product.price,
            "product_price_tier": product.price_tier.value if product.price_tier else "medium",

            # Request features
            "days_since_order": days_since_order,
            "order_amount": request.order_amount,
            "return_reason": request.return_reason.value,

            # Time features
            "request_hour": datetime.utcnow().hour,
            "request_day_of_week": datetime.utcnow().weekday(),
        }

    def _detect_risk_flags(
        self,
        buyer: Buyer,
        product: Product,
        request: ScoreRequest,
        days_since_order: int
    ) -> List[RiskFlag]:
        """Detect risk flags based on various indicators."""
        flags = []

        # High return rate flag
        if buyer.return_rate > 0.3:
            flags.append(RiskFlag(
                code="HIGH_RETURN_RATE",
                description=f"Buyer has {buyer.return_rate * 100:.1f}% return rate",
                severity="high"
            ))
        elif buyer.return_rate > 0.2:
            flags.append(RiskFlag(
                code="ELEVATED_RETURN_RATE",
                description=f"Buyer has {buyer.return_rate * 100:.1f}% return rate",
                severity="medium"
            ))

        # New account flag
        if buyer.account_age_days < 30:
            flags.append(RiskFlag(
                code="NEW_ACCOUNT",
                description="Account is less than 30 days old",
                severity="medium"
            ))

        # No reviews flag (potential bad actor)
        if buyer.total_orders > 5 and buyer.total_reviews == 0:
            flags.append(RiskFlag(
                code="NO_REVIEWS",
                description="Buyer has never left a review",
                severity="low"
            ))

        # Low review score
        if buyer.total_reviews > 0 and buyer.avg_review_score < 2.0:
            flags.append(RiskFlag(
                code="LOW_REVIEW_SCORE",
                description="Buyer gives consistently low reviews",
                severity="medium"
            ))

        # High value item
        if request.order_amount > 500:
            flags.append(RiskFlag(
                code="HIGH_VALUE_ITEM",
                description=f"Order value ${request.order_amount:.2f} exceeds $500",
                severity="medium"
            ))

        # Late return request
        return_window = product.custom_return_window or self.merchant.default_return_window
        if days_since_order > return_window:
            flags.append(RiskFlag(
                code="OUTSIDE_RETURN_WINDOW",
                description=f"Request is {days_since_order - return_window} days past return window",
                severity="high"
            ))
        elif days_since_order > return_window * 0.8:
            flags.append(RiskFlag(
                code="NEAR_WINDOW_END",
                description="Request near end of return window",
                severity="low"
            ))

        # Suspicious return reasons
        if request.return_reason == ReturnReason.CHANGED_MIND:
            if buyer.return_rate > 0.15:
                flags.append(RiskFlag(
                    code="FREQUENT_MIND_CHANGES",
                    description="Buyer frequently returns items due to changed mind",
                    severity="medium"
                ))

        # Multiple recent returns
        recent_returns = self.db.query(ReturnRequest).filter(
            ReturnRequest.buyer_id == buyer.id,
            ReturnRequest.request_date >= datetime.utcnow().replace(day=1)
        ).count()
        if recent_returns >= 3:
            flags.append(RiskFlag(
                code="MULTIPLE_RECENT_RETURNS",
                description=f"{recent_returns} returns this month",
                severity="high"
            ))

        return flags

    def _adjust_score(
        self,
        base_score: float,
        risk_flags: List[RiskFlag],
        within_window: bool
    ) -> float:
        """Adjust score based on risk flags."""
        score = base_score

        # Penalty for being outside return window
        if not within_window:
            score *= 0.5

        # Adjust based on flag severities
        for flag in risk_flags:
            if flag.severity == "high":
                score -= 15
            elif flag.severity == "medium":
                score -= 8
            elif flag.severity == "low":
                score -= 3

        # Ensure score stays in valid range
        return max(0, min(100, score))

    def _get_risk_level(self, score: float) -> RiskLevel:
        """Determine risk level from score."""
        if score >= settings.medium_risk_threshold:
            return RiskLevel.LOW
        elif score >= settings.high_risk_threshold:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.HIGH

    def _get_recommendation(
        self,
        score: float,
        risk_flags: List[RiskFlag]
    ) -> Recommendation:
        """Get recommendation based on score and flags."""
        # Check for any high severity flags
        high_severity_flags = [f for f in risk_flags if f.severity == "high"]

        if score < self.merchant.fraud_threshold:
            return Recommendation.DENY
        elif score >= self.merchant.auto_approve_threshold and not high_severity_flags:
            return Recommendation.APPROVE
        else:
            return Recommendation.REVIEW

    def _create_return_request(
        self,
        buyer: Buyer,
        product: Product,
        request: ScoreRequest,
        score: float,
        risk_level: RiskLevel,
        risk_flags: List[RiskFlag],
        confidence: float,
        recommendation: Recommendation
    ) -> ReturnRequest:
        """Create a return request record."""
        # Determine initial decision based on recommendation
        if recommendation == Recommendation.APPROVE:
            decision = ReturnDecision.APPROVED
            decided_by = "system"
        elif recommendation == Recommendation.DENY:
            decision = ReturnDecision.DENIED
            decided_by = "system"
        else:
            decision = ReturnDecision.REVIEW
            decided_by = None

        return_request = ReturnRequest(
            merchant_id=self.merchant.id,
            buyer_id=buyer.id,
            product_id=product.id,
            order_id=request.order_id,
            order_date=request.order_date,
            order_amount=request.order_amount,
            reason=request.return_reason,
            reason_details=request.reason_details,
            eligibility_score=score,
            risk_level=risk_level.value,
            risk_flags=json.dumps([f.model_dump() for f in risk_flags]),
            confidence=confidence,
            decision=decision,
            decided_at=datetime.utcnow() if decided_by else None,
            decided_by=decided_by,
        )
        self.db.add(return_request)
        self.db.commit()
        self.db.refresh(return_request)

        return return_request
