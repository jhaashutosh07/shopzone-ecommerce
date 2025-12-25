import os
import joblib
import numpy as np
from typing import Tuple, Optional

from app.ml.features import FeatureExtractor
from app.config import get_settings

settings = get_settings()


class MLPredictor:
    """ML model predictor for return eligibility scoring."""

    def __init__(self):
        self.feature_extractor = FeatureExtractor()
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load the trained model if it exists."""
        model_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            settings.model_path
        )
        if os.path.exists(model_path):
            try:
                self.model = joblib.load(model_path)
            except Exception as e:
                print(f"Warning: Could not load model: {e}")
                self.model = None

    def predict(self, raw_features: dict) -> Tuple[float, float]:
        """
        Predict return eligibility score.

        Args:
            raw_features: Dictionary of raw features

        Returns:
            Tuple of (score 0-100, confidence 0-1)
        """
        if self.model is None:
            # Fall back to rules-based scoring
            return self._rules_based_score(raw_features)

        try:
            # Extract features
            features = self.feature_extractor.extract(raw_features)

            # Get probability prediction
            if hasattr(self.model, 'predict_proba'):
                proba = self.model.predict_proba(features)[0]
                # Probability of class 1 (eligible)
                eligibility_prob = proba[1] if len(proba) > 1 else proba[0]
                score = eligibility_prob * 100

                # Confidence is how far from 0.5 the prediction is
                confidence = abs(eligibility_prob - 0.5) * 2
            else:
                # For models without predict_proba
                prediction = self.model.predict(features)[0]
                score = prediction * 100 if prediction <= 1 else prediction
                confidence = 0.7  # Default confidence

            return float(score), float(confidence)

        except Exception as e:
            print(f"Prediction error: {e}")
            return self._rules_based_score(raw_features)

    def _rules_based_score(self, features: dict) -> Tuple[float, float]:
        """
        Calculate score using rules-based approach (fallback).

        This provides a reasonable score when ML model is not available.
        """
        score = 70.0  # Base score
        confidence = 0.6  # Lower confidence for rules-based

        # Buyer return rate impact
        return_rate = features.get("buyer_return_rate", 0)
        if return_rate > 0.3:
            score -= 25
        elif return_rate > 0.2:
            score -= 15
        elif return_rate > 0.1:
            score -= 5
        elif return_rate < 0.05:
            score += 10

        # Account age impact
        account_age = features.get("buyer_account_age_days", 0)
        if account_age < 30:
            score -= 15
        elif account_age < 90:
            score -= 5
        elif account_age > 365:
            score += 10

        # Review score impact
        review_score = features.get("buyer_avg_review_score", 0)
        if review_score > 0:
            if review_score < 2:
                score -= 10
            elif review_score > 4:
                score += 10

        # Days since order impact
        days = features.get("days_since_order", 0)
        if days > 30:
            score -= 20
        elif days > 20:
            score -= 10
        elif days < 7:
            score += 5

        # Order amount impact
        amount = features.get("order_amount", 0)
        if amount > 500:
            score -= 10
        elif amount > 1000:
            score -= 20

        # Return reason impact
        reason = features.get("return_reason", "")
        if reason == "defective" or reason == "damaged_in_shipping":
            score += 15
        elif reason == "changed_mind":
            score -= 10

        # Product category risk
        category_risk = features.get("product_category_risk", 0.5)
        score += (0.5 - category_risk) * 20

        # Ensure score is within bounds
        score = max(0, min(100, score))

        return score, confidence

    def batch_predict(self, features_list: list) -> list:
        """Predict scores for multiple samples."""
        return [self.predict(f) for f in features_list]
