import numpy as np
import pandas as pd
from typing import Dict, List, Any

# Feature definitions for the ML model
NUMERICAL_FEATURES = [
    "buyer_return_rate",
    "buyer_total_orders",
    "buyer_total_returns",
    "buyer_avg_review_score",
    "buyer_account_age_days",
    "buyer_total_spend",
    "product_return_rate",
    "product_category_risk",
    "product_price",
    "days_since_order",
    "order_amount",
    "request_hour",
    "request_day_of_week",
]

CATEGORICAL_FEATURES = [
    "product_price_tier",
    "return_reason",
]

PRICE_TIER_MAP = {
    "low": 0,
    "medium": 1,
    "high": 2,
    "premium": 3,
}

RETURN_REASON_MAP = {
    "size_issue": 0,
    "defective": 1,
    "not_as_described": 2,
    "changed_mind": 3,
    "arrived_late": 4,
    "damaged_in_shipping": 5,
    "wrong_item": 6,
    "other": 7,
}


class FeatureExtractor:
    """Extract and transform features for ML model."""

    def __init__(self):
        self.feature_names = NUMERICAL_FEATURES + ["price_tier_encoded", "return_reason_encoded"]

    def extract(self, raw_features: Dict[str, Any]) -> np.ndarray:
        """Extract features from raw input dictionary."""
        features = []

        # Numerical features
        for feat in NUMERICAL_FEATURES:
            value = raw_features.get(feat, 0)
            if value is None:
                value = 0
            features.append(float(value))

        # Encode categorical features
        price_tier = raw_features.get("product_price_tier", "medium")
        features.append(float(PRICE_TIER_MAP.get(price_tier, 1)))

        return_reason = raw_features.get("return_reason", "other")
        features.append(float(RETURN_REASON_MAP.get(return_reason, 7)))

        return np.array(features).reshape(1, -1)

    def extract_batch(self, raw_features_list: List[Dict[str, Any]]) -> np.ndarray:
        """Extract features for multiple samples."""
        return np.vstack([self.extract(f) for f in raw_features_list])

    def to_dataframe(self, raw_features: Dict[str, Any]) -> pd.DataFrame:
        """Convert features to DataFrame for analysis."""
        features = self.extract(raw_features)
        return pd.DataFrame(features, columns=self.feature_names)


def generate_synthetic_features(n_samples: int = 1000, fraud_ratio: float = 0.2) -> tuple:
    """Generate synthetic training data for initial model."""
    np.random.seed(42)

    n_fraud = int(n_samples * fraud_ratio)
    n_legit = n_samples - n_fraud

    data = []
    labels = []

    # Generate legitimate returns
    for _ in range(n_legit):
        sample = {
            "buyer_return_rate": np.random.beta(2, 8),  # Low return rate
            "buyer_total_orders": np.random.randint(5, 100),
            "buyer_total_returns": np.random.randint(0, 10),
            "buyer_avg_review_score": np.random.uniform(3.5, 5.0),
            "buyer_account_age_days": np.random.randint(90, 1000),
            "buyer_total_spend": np.random.uniform(200, 5000),
            "product_return_rate": np.random.beta(2, 10),
            "product_category_risk": np.random.uniform(0.2, 0.7),
            "product_price": np.random.uniform(20, 300),
            "days_since_order": np.random.randint(1, 25),
            "order_amount": np.random.uniform(30, 400),
            "request_hour": np.random.randint(8, 22),
            "request_day_of_week": np.random.randint(0, 7),
            "product_price_tier": np.random.choice(["low", "medium", "high"]),
            "return_reason": np.random.choice([
                "size_issue", "defective", "not_as_described", "damaged_in_shipping"
            ]),
        }
        data.append(sample)
        labels.append(1)  # 1 = eligible for return

    # Generate fraudulent/ineligible returns
    for _ in range(n_fraud):
        sample = {
            "buyer_return_rate": np.random.beta(5, 3),  # High return rate
            "buyer_total_orders": np.random.randint(1, 20),
            "buyer_total_returns": np.random.randint(5, 15),
            "buyer_avg_review_score": np.random.uniform(1.0, 3.0),
            "buyer_account_age_days": np.random.randint(1, 60),
            "buyer_total_spend": np.random.uniform(50, 500),
            "product_return_rate": np.random.beta(5, 5),
            "product_category_risk": np.random.uniform(0.5, 0.9),
            "product_price": np.random.uniform(200, 800),
            "days_since_order": np.random.randint(25, 60),
            "order_amount": np.random.uniform(300, 1000),
            "request_hour": np.random.choice([2, 3, 4, 5, 23, 0, 1]),  # Odd hours
            "request_day_of_week": np.random.randint(0, 7),
            "product_price_tier": np.random.choice(["high", "premium"]),
            "return_reason": np.random.choice(["changed_mind", "other"]),
        }
        data.append(sample)
        labels.append(0)  # 0 = not eligible

    return data, labels
