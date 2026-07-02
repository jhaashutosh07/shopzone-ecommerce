"""Startup bootstrap: schema upgrades, model provisioning, demo merchant.

Goal: `docker compose up` yields a fully working system with a trained
model and a ready-to-use demo merchant + API key, no manual steps.
"""
import os
import json
from datetime import datetime

from sqlalchemy import text, inspect
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.merchant import Merchant
from app.models.scoring_model import ScoringModel
from app.services.auth import AuthService
from app.ml.train import ModelTrainer, default_model_path
from app.ml.predict import get_predictor

settings = get_settings()

# Columns added after the initial release; applied idempotently on boot so
# existing databases upgrade without Alembic.
SCHEMA_UPGRADES = [
    ("return_requests", "explanation", "TEXT"),
    ("return_requests", "features_snapshot", "TEXT"),
    ("return_requests", "model_version", "INTEGER"),
    ("scoring_models", "feedback_samples", "INTEGER"),
    ("scoring_models", "roc_auc", "FLOAT"),
]


def ensure_schema(engine):
    """Add columns introduced by newer versions to existing tables."""
    inspector = inspect(engine)
    with engine.connect() as conn:
        for table, column, col_type in SCHEMA_UPGRADES:
            if table not in inspector.get_table_names():
                continue
            existing = {c["name"] for c in inspector.get_columns(table)}
            if column not in existing:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"))
                conn.commit()
                print(f"Schema upgrade: added {table}.{column}")


def ensure_model(db: Session):
    """Make sure a trained model is available and registered.

    Whichever is newer wins: the registry's active version or the file
    artifact (e.g. retrained offline via `python -m app.ml.train`).
    """
    model_path = default_model_path()
    active = (
        db.query(ScoringModel)
        .filter(ScoringModel.is_active == True, ScoringModel.model_blob.isnot(None))
        .order_by(ScoringModel.version.desc())
        .first()
    )

    predictor = get_predictor()
    predictor.reload()
    file_version = predictor.version if predictor.bundle else None

    if active is not None and (file_version is None or active.version > file_version):
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        with open(model_path, "wb") as f:
            f.write(active.model_blob)
        predictor.reload()
        print(f"Restored scoring model v{active.version} from registry")
        return

    if os.path.exists(model_path):
        if active is None or (file_version is not None and file_version > active.version):
            _register_existing_artifact(db, deactivate_others=active is not None)
        return

    print("No scoring model found - training initial model...")
    trainer = ModelTrainer()
    metrics = trainer.train(n_synthetic_samples=5000, version=1, run_cv=False)
    trainer.save_model()
    record = ScoringModel(
        version=1,
        model_type="gradient_boosting",
        model_blob=trainer.serialize_bundle(),
        features_used=json.dumps(trainer.feature_extractor.feature_names),
        training_samples=metrics["training_samples"],
        feedback_samples=0,
        accuracy=metrics["accuracy"],
        precision_score=metrics["precision"],
        recall_score=metrics["recall"],
        f1_score=metrics["f1"],
        roc_auc=metrics["roc_auc"],
        is_active=True,
        trained_at=datetime.utcnow(),
    )
    db.add(record)
    db.commit()
    get_predictor().reload()
    print("Initial model v1 trained, saved, and registered")


def _register_existing_artifact(db: Session, deactivate_others: bool = False):
    """Import a file artifact into the registry (newer than what's there)."""
    predictor = get_predictor()
    predictor.reload()
    if predictor.bundle is None:
        return  # legacy bare-model artifact; leave as-is, serving still works
    if deactivate_others:
        db.query(ScoringModel).filter(ScoringModel.is_active == True).update(
            {"is_active": False}
        )

    bundle = predictor.bundle
    metrics = bundle.get("metrics", {})
    with open(default_model_path(), "rb") as f:
        blob = f.read()
    record = ScoringModel(
        version=bundle.get("version", 1),
        model_type="gradient_boosting",
        model_blob=blob,
        features_used=json.dumps(bundle.get("feature_names", [])),
        training_samples=metrics.get("training_samples", 0),
        feedback_samples=metrics.get("feedback_samples", 0),
        accuracy=metrics.get("accuracy"),
        precision_score=metrics.get("precision"),
        recall_score=metrics.get("recall"),
        f1_score=metrics.get("f1"),
        roc_auc=metrics.get("roc_auc"),
        is_active=True,
        trained_at=datetime.fromisoformat(bundle["trained_at"]) if bundle.get("trained_at") else None,
    )
    db.add(record)
    db.commit()
    print(f"Registered existing model artifact as v{record.version}")


def ensure_demo_merchant(db: Session):
    """Provision the demo merchant with a deterministic API key.

    The storefront container receives the same key via env, so the two
    services are integrated out of the box.
    """
    if not settings.demo_merchant_email or not settings.demo_api_key:
        return

    merchant = db.query(Merchant).filter(
        Merchant.email == settings.demo_merchant_email
    ).first()

    if merchant is None:
        merchant = Merchant(
            name=settings.demo_merchant_name,
            email=settings.demo_merchant_email,
            password_hash=AuthService.hash_password(settings.demo_merchant_password),
        )
        db.add(merchant)
        print(f"Created demo merchant {settings.demo_merchant_email}")

    expected_hash = AuthService.hash_api_key(settings.demo_api_key)
    if merchant.api_key_hash != expected_hash:
        merchant.api_key_hash = expected_hash
        print("Demo merchant API key provisioned")
    db.commit()


def run_bootstrap(engine, SessionLocal):
    ensure_schema(engine)
    db = SessionLocal()
    try:
        ensure_demo_merchant(db)
        if settings.bootstrap_train:
            ensure_model(db)
    finally:
        db.close()
