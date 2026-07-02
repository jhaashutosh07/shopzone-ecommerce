import os
import io
import joblib
import numpy as np
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple

from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)

from app.ml.features import FeatureExtractor, generate_synthetic_features
from app.ml.ecommerce_data import generate_flipkart_amazon_dataset, generate_test_scenarios
from app.ml.explain import build_histograms
from app.config import get_settings

settings = get_settings()

# How many times each merchant-feedback sample is repeated during training.
# Feedback is scarce but is real ground truth, so it gets extra weight.
FEEDBACK_WEIGHT = 5


def default_model_path() -> str:
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    return os.path.join(base_dir, settings.model_path)


class ModelTrainer:
    """Train and evaluate ML models for return eligibility scoring."""

    def __init__(self):
        self.feature_extractor = FeatureExtractor()
        self.model = None
        self.bundle: Optional[Dict[str, Any]] = None
        self.metrics: Dict[str, float] = {}

    def train(
        self,
        data: Optional[list] = None,
        labels: Optional[list] = None,
        n_synthetic_samples: int = 5000,
        test_size: float = 0.2,
        feedback_data: Optional[List[dict]] = None,
        feedback_labels: Optional[List[int]] = None,
        version: int = 1,
        run_cv: bool = True,
    ) -> Dict[str, Any]:
        """
        Train the model on provided or synthetic data, optionally mixed with
        merchant-feedback ground truth (manual approve/deny overrides).

        Returns a dictionary with training results and metrics.
        """
        if data is None or labels is None:
            print(f"Generating {n_synthetic_samples} Flipkart/Amazon samples...")
            data, labels = generate_flipkart_amazon_dataset(n_synthetic_samples)

        n_feedback = 0
        if feedback_data and feedback_labels:
            n_feedback = len(feedback_data)
            print(f"Mixing in {n_feedback} merchant-feedback samples (x{FEEDBACK_WEIGHT} weight)...")
            data = list(data) + list(feedback_data) * FEEDBACK_WEIGHT
            labels = list(labels) + list(feedback_labels) * FEEDBACK_WEIGHT

        print("Extracting features...")
        X = self.feature_extractor.extract_batch(data)
        y = np.array(labels)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )

        print("Training Gradient Boosting model...")
        self.model = GradientBoostingClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=42
        )
        self.model.fit(X_train, y_train)

        y_pred = self.model.predict(X_test)
        y_proba = self.model.predict_proba(X_test)[:, 1]

        self.metrics = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred)),
            "recall": float(recall_score(y_test, y_pred)),
            "f1": float(f1_score(y_test, y_pred)),
            "roc_auc": float(roc_auc_score(y_test, y_proba)),
            "training_samples": int(len(X_train)),
            "test_samples": int(len(X_test)),
            "feedback_samples": int(n_feedback),
        }

        if run_cv:
            cv_scores = cross_val_score(self.model, X, y, cv=5)
            self.metrics["cv_mean"] = float(cv_scores.mean())
            self.metrics["cv_std"] = float(cv_scores.std())

        # Everything the serving/explain/drift layers need travels with the model
        baselines = np.median(X, axis=0)
        self.bundle = {
            "model": self.model,
            "feature_names": self.feature_extractor.feature_names,
            "baselines": baselines.tolist(),
            "histograms": build_histograms(X, self.feature_extractor.feature_names),
            "metrics": self.metrics,
            "version": version,
            "trained_at": datetime.utcnow().isoformat(),
        }

        print("Training complete!")
        print(f"Accuracy: {self.metrics['accuracy']:.3f}")
        print(f"Precision: {self.metrics['precision']:.3f}")
        print(f"Recall: {self.metrics['recall']:.3f}")
        print(f"F1 Score: {self.metrics['f1']:.3f}")
        print(f"ROC-AUC: {self.metrics['roc_auc']:.3f}")
        if run_cv:
            print(f"CV Score: {self.metrics['cv_mean']:.3f} (+/- {self.metrics['cv_std']:.3f})")

        return self.metrics

    def save_model(self, path: Optional[str] = None) -> str:
        """Save the trained model bundle to disk."""
        if self.bundle is None:
            raise ValueError("No model to save. Train first.")

        if path is None:
            path = default_model_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)

        joblib.dump(self.bundle, path)
        print(f"Model bundle saved to {path}")
        return path

    def serialize_bundle(self) -> bytes:
        """Serialize the bundle for database storage (model registry)."""
        if self.bundle is None:
            raise ValueError("No model to serialize. Train first.")
        buffer = io.BytesIO()
        joblib.dump(self.bundle, buffer)
        return buffer.getvalue()

    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from trained model."""
        if self.model is None:
            raise ValueError("No model trained yet.")

        importance = dict(zip(
            self.feature_extractor.feature_names,
            self.model.feature_importances_
        ))
        return dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))


def validate_model(trainer: ModelTrainer) -> None:
    """Validate model with test scenarios."""
    scenarios = generate_test_scenarios()
    print("\n" + "=" * 50)
    print("Validating with test scenarios:")
    print("=" * 50)

    for scenario in scenarios:
        features = trainer.feature_extractor.extract(scenario["features"])
        prediction = trainer.model.predict(features)[0]
        proba = trainer.model.predict_proba(features)[0]

        result = "ELIGIBLE" if prediction == 1 else "NOT ELIGIBLE"
        confidence = proba[prediction] * 100

        status = "PASS" if (
            (scenario["expected"] == "APPROVE" and prediction == 1) or
            (scenario["expected"] == "DENY" and prediction == 0) or
            (scenario["expected"] == "REVIEW" and proba[1] > 0.3 and proba[1] < 0.7)
        ) else "REVIEW"

        print(f"\n{scenario['name']}:")
        print(f"  Expected: {scenario['expected']}")
        print(f"  Predicted: {result} (confidence: {confidence:.1f}%)")
        print(f"  Status: {status}")


def train_and_save_model(n_samples: int = 10000, run_cv: bool = True) -> Tuple[str, Dict[str, float]]:
    """Convenience function to train and save a model."""
    print("=" * 50)
    print("Return Policy Engine - ML Model Training")
    print("=" * 50)

    trainer = ModelTrainer()
    metrics = trainer.train(n_synthetic_samples=n_samples, run_cv=run_cv)
    model_path = trainer.save_model()

    print("\n" + "=" * 50)
    print("Feature Importance:")
    print("=" * 50)
    for name, importance in trainer.get_feature_importance().items():
        print(f"  {name}: {importance:.4f}")

    validate_model(trainer)

    print("\n" + "=" * 50)
    print(f"Model saved to: {model_path}")
    print("Training complete!")
    print("=" * 50)

    return model_path, metrics


if __name__ == "__main__":
    train_and_save_model(n_samples=10000)
