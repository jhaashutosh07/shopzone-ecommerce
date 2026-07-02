"""Per-decision explainability for the scoring model.

Produces feature contributions in score points (0-100 scale) using
interventional ablation: each feature is replaced by its training-set
baseline (median) and the resulting probability shift is attributed to
that feature. This is model-agnostic and requires no extra dependencies.
"""
import numpy as np
from typing import Any, Dict, List

from app.ml.features import NUMERICAL_FEATURES

# Human-readable labels shown to merchants and buyers
FEATURE_LABELS: Dict[str, str] = {
    "buyer_return_rate": "Buyer return rate",
    "buyer_total_orders": "Buyer order history",
    "buyer_total_returns": "Buyer total returns",
    "buyer_avg_review_score": "Buyer review score",
    "buyer_account_age_days": "Account age",
    "buyer_total_spend": "Buyer lifetime spend",
    "product_return_rate": "Product return rate",
    "product_category_risk": "Product category risk",
    "product_price": "Product price",
    "days_since_order": "Days since order",
    "order_amount": "Order amount",
    "request_hour": "Request time of day",
    "request_day_of_week": "Request day of week",
    "price_tier_encoded": "Product price tier",
    "return_reason_encoded": "Return reason",
}

# Raw feature key used to display the original (unencoded) value
DISPLAY_VALUE_KEY: Dict[str, str] = {
    "price_tier_encoded": "product_price_tier",
    "return_reason_encoded": "return_reason",
}


def _display_value(feature_name: str, raw_features: Dict[str, Any], encoded_value: float) -> str:
    raw_key = DISPLAY_VALUE_KEY.get(feature_name, feature_name)
    value = raw_features.get(raw_key, encoded_value)
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def explain_prediction(
    model,
    feature_vector: np.ndarray,
    baselines: List[float],
    feature_names: List[str],
    raw_features: Dict[str, Any],
    top_k: int = 6,
) -> List[Dict[str, Any]]:
    """Attribute the model score to individual features via baseline ablation.

    Returns the top_k contributions sorted by absolute impact, each in
    score points: positive = pushed the score up (more eligible),
    negative = pushed the score down (more risky).
    """
    base_prob = float(model.predict_proba(feature_vector)[0][1])

    contributions = []
    for idx, name in enumerate(feature_names):
        actual = float(feature_vector[0, idx])
        baseline = float(baselines[idx])
        if actual == baseline:
            continue

        ablated = feature_vector.copy()
        ablated[0, idx] = baseline
        ablated_prob = float(model.predict_proba(ablated)[0][1])
        delta_points = (base_prob - ablated_prob) * 100

        if abs(delta_points) < 0.05:
            continue

        contributions.append({
            "feature": name,
            "label": FEATURE_LABELS.get(name, name),
            "value": _display_value(name, raw_features, actual),
            "contribution": round(delta_points, 2),
            "direction": "positive" if delta_points >= 0 else "negative",
        })

    contributions.sort(key=lambda c: abs(c["contribution"]), reverse=True)
    return contributions[:top_k]


def compute_psi(
    train_proportions: List[float],
    bin_edges: List[float],
    recent_values: List[float],
) -> float:
    """Population Stability Index between training and recent distributions.

    < 0.1 stable, 0.1-0.25 moderate shift, > 0.25 significant drift.
    """
    eps = 1e-4
    edges = np.array(bin_edges)
    counts, _ = np.histogram(np.array(recent_values, dtype=float), bins=edges)
    total = counts.sum()
    if total == 0:
        return 0.0
    recent_props = counts / total

    psi = 0.0
    for p_train, p_recent in zip(train_proportions, recent_props):
        p_t = max(float(p_train), eps)
        p_r = max(float(p_recent), eps)
        psi += (p_r - p_t) * np.log(p_r / p_t)
    return float(psi)


def build_histograms(X: np.ndarray, feature_names: List[str], n_bins: int = 10) -> Dict[str, Dict]:
    """Store per-feature training distributions for later drift comparison."""
    histograms = {}
    for idx, name in enumerate(feature_names):
        if name not in NUMERICAL_FEATURES:
            continue
        values = X[:, idx]
        # Guard degenerate features with a single unique value
        if np.min(values) == np.max(values):
            edges = np.array([np.min(values) - 0.5, np.max(values) + 0.5])
        else:
            edges = np.histogram_bin_edges(values, bins=n_bins)
        counts, _ = np.histogram(values, bins=edges)
        histograms[name] = {
            "bin_edges": edges.tolist(),
            "proportions": (counts / counts.sum()).tolist(),
        }
    return histograms
