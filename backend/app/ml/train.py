import os
import joblib
import numpy as np
from datetime import datetime
from typing import Optional, Dict, Any

from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from app.ml.features import FeatureExtractor, generate_synthetic_features
from app.ml.ecommerce_data import generate_flipkart_amazon_dataset, generate_test_scenarios
from app.config import get_settings

settings = get_settings()


class ModelTrainer:
    """Train and evaluate ML models for return eligibility scoring."""

    def __init__(self):
        self.feature_extractor = FeatureExtractor()
        self.model = None
        self.metrics: Dict[str, float] = {}

    def train(
        self,
        data: Optional[list] = None,
        labels: Optional[list] = None,
        n_synthetic_samples: int = 5000,
        test_size: float = 0.2
    ) -> Dict[str, Any]:
        """
        Train the model on provided or synthetic data.

        Args:
            data: List of feature dictionaries (optional)
            labels: List of labels 0/1 (optional)
            n_synthetic_samples: Number of synthetic samples if no data provided
            test_size: Fraction of data for testing

        Returns:
            Dictionary with training results and metrics
        """
        # Generate synthetic data if none provided
        if data is None or labels is None:
            print(f"Generating {n_synthetic_samples} Flipkart/Amazon samples...")
            data, labels = generate_flipkart_amazon_dataset(n_synthetic_samples)

        # Extract features
        print("Extracting features...")
        X = self.feature_extractor.extract_batch(data)
        y = np.array(labels)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )

        # Initialize model
        print("Training Gradient Boosting model...")
        self.model = GradientBoostingClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=42
        )

        # Train
        self.model.fit(X_train, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test)
        y_proba = self.model.predict_proba(X_test)[:, 1]

        self.metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred),
            "recall": recall_score(y_test, y_pred),
            "f1": f1_score(y_test, y_pred),
            "training_samples": len(X_train),
            "test_samples": len(X_test),
        }

        # Cross-validation
        cv_scores = cross_val_score(self.model, X, y, cv=5)
        self.metrics["cv_mean"] = cv_scores.mean()
        self.metrics["cv_std"] = cv_scores.std()

        print(f"Training complete!")
        print(f"Accuracy: {self.metrics['accuracy']:.3f}")
        print(f"Precision: {self.metrics['precision']:.3f}")
        print(f"Recall: {self.metrics['recall']:.3f}")
        print(f"F1 Score: {self.metrics['f1']:.3f}")
        print(f"CV Score: {self.metrics['cv_mean']:.3f} (+/- {self.metrics['cv_std']:.3f})")

        return self.metrics

    def save_model(self, path: Optional[str] = None) -> str:
        """Save the trained model to disk."""
        if self.model is None:
            raise ValueError("No model to save. Train first.")

        if path is None:
            # Default path
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            model_dir = os.path.join(base_dir, "ml", "models")
            os.makedirs(model_dir, exist_ok=True)
            path = os.path.join(model_dir, "scoring_model.joblib")

        joblib.dump(self.model, path)
        print(f"Model saved to {path}")
        return path

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


def train_and_save_model(n_samples: int = 10000):
    """Convenience function to train and save a model."""
    print("=" * 50)
    print("Return Policy Engine - ML Model Training")
    print("Using Flipkart/Amazon E-commerce Data")
    print("=" * 50)

    trainer = ModelTrainer()
    metrics = trainer.train(n_synthetic_samples=n_samples)
    model_path = trainer.save_model()

    # Print feature importance
    print("\n" + "=" * 50)
    print("Feature Importance:")
    print("=" * 50)
    for name, importance in trainer.get_feature_importance().items():
        print(f"  {name}: {importance:.4f}")

    # Validate with test scenarios
    validate_model(trainer)

    print("\n" + "=" * 50)
    print(f"Model saved to: {model_path}")
    print("Training complete!")
    print("=" * 50)

    return model_path, metrics


if __name__ == "__main__":
    train_and_save_model(n_samples=10000)
