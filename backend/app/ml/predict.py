import os
import joblib
import numpy as np
from typing import Tuple, Optional, List, Dict, Any

from app.ml.features import FeatureExtractor
from app.ml.explain import explain_prediction, FEATURE_LABELS
from app.config import get_settings

settings = get_settings()


class MLPredictor:
    """ML model predictor for return eligibility scoring.

    Loads a model bundle (model + baselines + training histograms + metadata)
    produced by ModelTrainer. Falls back to rules-based scoring when no
    trained model is available. Use get_predictor() to share one instance
    across requests; call reload() after retraining.
    """

    def __init__(self):
        self.feature_extractor = FeatureExtractor()
        self.model = None
        self.bundle: Optional[Dict[str, Any]] = None
        self._load_model()

    @property
    def model_path(self) -> str:
        return os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            settings.model_path
        )

    def _load_model(self):
        """Load the trained model bundle if it exists."""
        if not os.path.exists(self.model_path):
            return
        try:
            loaded = joblib.load(self.model_path)
            if isinstance(loaded, dict) and "model" in loaded:
                self.bundle = loaded
                self.model = loaded["model"]
            else:
                # Legacy artifact: bare sklearn model without metadata
                self.model = loaded
                self.bundle = None
        except Exception as e:
            print(f"Warning: Could not load model: {e}")
            self.model = None
            self.bundle = None

    def reload(self):
        """Re-read the model artifact from disk (after retraining)."""
        self.model = None
        self.bundle = None
        self._load_model()

    @property
    def is_ml(self) -> bool:
        return self.model is not None

    @property
    def version(self) -> Optional[int]:
        if self.bundle:
            return self.bundle.get("version")
        return None

    @property
    def metrics(self) -> Optional[Dict[str, float]]:
        if self.bundle:
            return self.bundle.get("metrics")
        return None

    @property
    def histograms(self) -> Optional[Dict[str, Dict]]:
        if self.bundle:
            return self.bundle.get("histograms")
        return None

    def predict(self, raw_features: dict) -> Tuple[float, float]:
        """
        Predict return eligibility score.

        Returns:
            Tuple of (score 0-100, confidence 0-1)
        """
        if self.model is None:
            score, confidence, _ = self._rules_based_score(raw_features)
            return score, confidence

        try:
            features = self.feature_extractor.extract(raw_features)

            if hasattr(self.model, 'predict_proba'):
                proba = self.model.predict_proba(features)[0]
                eligibility_prob = proba[1] if len(proba) > 1 else proba[0]
                score = eligibility_prob * 100
                # Confidence is how far from 0.5 the prediction is
                confidence = abs(eligibility_prob - 0.5) * 2
            else:
                prediction = self.model.predict(features)[0]
                score = prediction * 100 if prediction <= 1 else prediction
                confidence = 0.7

            return float(score), float(confidence)

        except Exception as e:
            print(f"Prediction error: {e}")
            score, confidence, _ = self._rules_based_score(raw_features)
            return score, confidence

    def explain(self, raw_features: dict) -> List[Dict[str, Any]]:
        """Return the top feature contributions for this prediction,
        in score points (positive = raised the score)."""
        if self.model is not None and self.bundle is not None:
            try:
                features = self.feature_extractor.extract(raw_features)
                return explain_prediction(
                    model=self.model,
                    feature_vector=features,
                    baselines=self.bundle["baselines"],
                    feature_names=self.bundle["feature_names"],
                    raw_features=raw_features,
                )
            except Exception as e:
                print(f"Explanation error: {e}")

        # Rules fallback (also used for legacy artifacts without baselines)
        _, _, contributions = self._rules_based_score(raw_features)
        return contributions

    def _rules_based_score(self, features: dict) -> Tuple[float, float, List[Dict[str, Any]]]:
        """
        Calculate score using rules-based approach (fallback).

        Also collects each rule's score delta so decisions stay explainable
        even without a trained model.
        """
        score = 70.0  # Base score
        confidence = 0.6  # Lower confidence for rules-based
        contributions: List[Dict[str, Any]] = []

        def apply(feature: str, value, delta: float):
            nonlocal score
            if delta == 0:
                return
            score += delta
            contributions.append({
                "feature": feature,
                "label": FEATURE_LABELS.get(feature, feature),
                "value": f"{value:.2f}" if isinstance(value, float) else str(value),
                "contribution": round(delta, 2),
                "direction": "positive" if delta >= 0 else "negative",
            })

        # Buyer return rate impact
        return_rate = features.get("buyer_return_rate", 0)
        if return_rate > 0.3:
            apply("buyer_return_rate", return_rate, -25)
        elif return_rate > 0.2:
            apply("buyer_return_rate", return_rate, -15)
        elif return_rate > 0.1:
            apply("buyer_return_rate", return_rate, -5)
        elif return_rate < 0.05:
            apply("buyer_return_rate", return_rate, +10)

        # Account age impact
        account_age = features.get("buyer_account_age_days", 0)
        if account_age < 30:
            apply("buyer_account_age_days", account_age, -15)
        elif account_age < 90:
            apply("buyer_account_age_days", account_age, -5)
        elif account_age > 365:
            apply("buyer_account_age_days", account_age, +10)

        # Review score impact
        review_score = features.get("buyer_avg_review_score", 0)
        if review_score > 0:
            if review_score < 2:
                apply("buyer_avg_review_score", review_score, -10)
            elif review_score > 4:
                apply("buyer_avg_review_score", review_score, +10)

        # Days since order impact
        days = features.get("days_since_order", 0)
        if days > 30:
            apply("days_since_order", days, -20)
        elif days > 20:
            apply("days_since_order", days, -10)
        elif days < 7:
            apply("days_since_order", days, +5)

        # Order amount impact
        amount = features.get("order_amount", 0)
        if amount > 1000:
            apply("order_amount", amount, -20)
        elif amount > 500:
            apply("order_amount", amount, -10)

        # Return reason impact
        reason = features.get("return_reason", "")
        if reason == "defective" or reason == "damaged_in_shipping":
            apply("return_reason_encoded", reason, +15)
        elif reason == "changed_mind":
            apply("return_reason_encoded", reason, -10)

        # Product category risk
        category_risk = features.get("product_category_risk", 0.5)
        apply("product_category_risk", category_risk, (0.5 - category_risk) * 20)

        # Ensure score is within bounds
        score = max(0, min(100, score))

        contributions.sort(key=lambda c: abs(c["contribution"]), reverse=True)
        return score, confidence, contributions[:6]

    def batch_predict(self, features_list: list) -> list:
        """Predict scores for multiple samples."""
        return [self.predict(f) for f in features_list]


_predictor: Optional[MLPredictor] = None


def get_predictor() -> MLPredictor:
    """Process-wide predictor instance (model loads are expensive)."""
    global _predictor
    if _predictor is None:
        _predictor = MLPredictor()
    return _predictor
