"""Model registry, feedback-driven retraining, and drift monitoring.

The feedback loop: every time a merchant manually overrides a system
decision (approve/deny), that return request becomes a labeled ground-truth
sample. Retraining mixes those samples into the training set at elevated
weight, registers a new model version, and hot-swaps the serving model.
"""
import json
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.merchant import Merchant
from app.models.return_request import ReturnRequest, ReturnDecision
from app.models.scoring_model import ScoringModel
from app.schemas.scoring import (
    ModelVersionInfo,
    RetrainResponse,
    DriftReport,
    FeatureDrift,
)
from app.services.auth import get_current_merchant
from app.ml.train import ModelTrainer
from app.ml.predict import get_predictor
from app.ml.explain import compute_psi, FEATURE_LABELS

router = APIRouter(prefix="/models", tags=["Model Registry"])

MIN_DRIFT_SAMPLES = 30
DRIFT_WINDOW = 500


def _collect_feedback_samples(db: Session):
    """Return requests where a human overrode (or confirmed) the decision.

    decided_by == "system" means the model decided; anything else is a
    merchant action and counts as ground truth. approved -> 1, denied -> 0.
    """
    rows = db.query(ReturnRequest).filter(
        ReturnRequest.features_snapshot.isnot(None),
        ReturnRequest.decided_by.isnot(None),
        ReturnRequest.decided_by != "system",
        ReturnRequest.decision.in_([ReturnDecision.APPROVED, ReturnDecision.DENIED]),
    ).all()

    data, labels = [], []
    for row in rows:
        try:
            features = json.loads(row.features_snapshot)
        except (json.JSONDecodeError, TypeError):
            continue
        data.append(features)
        labels.append(1 if row.decision == ReturnDecision.APPROVED else 0)
    return data, labels


def _to_version_info(record: ScoringModel) -> ModelVersionInfo:
    return ModelVersionInfo(
        id=record.id,
        version=record.version,
        model_type=record.model_type,
        is_active=record.is_active,
        training_samples=record.training_samples or 0,
        feedback_samples=record.feedback_samples or 0,
        accuracy=record.accuracy,
        precision_score=record.precision_score,
        recall_score=record.recall_score,
        f1_score=record.f1_score,
        roc_auc=record.roc_auc,
        trained_at=record.trained_at,
        created_at=record.created_at,
    )


@router.get("", response_model=List[ModelVersionInfo])
def list_models(
    merchant: Merchant = Depends(get_current_merchant),
    db: Session = Depends(get_db),
):
    """List all registered model versions, newest first."""
    records = db.query(ScoringModel).order_by(ScoringModel.version.desc()).all()
    return [_to_version_info(r) for r in records]


@router.post("/retrain", response_model=RetrainResponse)
def retrain_model(
    merchant: Merchant = Depends(get_current_merchant),
    db: Session = Depends(get_db),
):
    """Retrain the scoring model using accumulated merchant feedback.

    Registers the new version and immediately activates it for serving.
    """
    feedback_data, feedback_labels = _collect_feedback_samples(db)

    max_version = db.query(ScoringModel).order_by(ScoringModel.version.desc()).first()
    new_version = (max_version.version + 1) if max_version else 1

    trainer = ModelTrainer()
    metrics = trainer.train(
        n_synthetic_samples=5000,
        feedback_data=feedback_data,
        feedback_labels=feedback_labels,
        version=new_version,
        run_cv=False,
    )

    # Register in DB (durable) and write the serving artifact (fast path)
    db.query(ScoringModel).filter(ScoringModel.is_active == True).update(
        {"is_active": False}
    )
    record = ScoringModel(
        version=new_version,
        model_type="gradient_boosting",
        model_blob=trainer.serialize_bundle(),
        features_used=json.dumps(trainer.feature_extractor.feature_names),
        training_samples=metrics["training_samples"],
        feedback_samples=metrics["feedback_samples"],
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

    trainer.save_model()
    get_predictor().reload()

    return RetrainResponse(
        version=new_version,
        metrics=metrics,
        feedback_samples=len(feedback_data),
        activated=True,
        message=f"Model v{new_version} trained on {metrics['training_samples']} samples "
                f"({len(feedback_data)} merchant-feedback) and activated.",
    )


@router.get("/drift", response_model=DriftReport)
def get_drift_report(
    merchant: Merchant = Depends(get_current_merchant),
    db: Session = Depends(get_db),
):
    """Compare recent scored traffic against the training distribution (PSI).

    PSI < 0.1 = stable, 0.1-0.25 = moderate shift, > 0.25 = drifted.
    """
    predictor = get_predictor()
    histograms = predictor.histograms
    if not histograms:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No trained model bundle available for drift comparison",
        )

    rows = (
        db.query(ReturnRequest.features_snapshot)
        .filter(
            ReturnRequest.merchant_id == merchant.id,
            ReturnRequest.features_snapshot.isnot(None),
        )
        .order_by(ReturnRequest.created_at.desc())
        .limit(DRIFT_WINDOW)
        .all()
    )

    snapshots = []
    for (snap,) in rows:
        try:
            snapshots.append(json.loads(snap))
        except (json.JSONDecodeError, TypeError):
            continue

    if len(snapshots) < MIN_DRIFT_SAMPLES:
        return DriftReport(
            model_version=predictor.version,
            samples_analyzed=len(snapshots),
            features=[],
            overall_status="insufficient_data",
        )

    features = []
    worst = "stable"
    rank = {"stable": 0, "moderate": 1, "drifted": 2}
    for name, hist in histograms.items():
        values = [float(s[name]) for s in snapshots if s.get(name) is not None]
        if not values:
            continue
        psi = compute_psi(hist["proportions"], hist["bin_edges"], values)
        if psi > 0.25:
            feature_status = "drifted"
        elif psi > 0.1:
            feature_status = "moderate"
        else:
            feature_status = "stable"
        if rank[feature_status] > rank[worst]:
            worst = feature_status
        features.append(FeatureDrift(
            feature=name,
            label=FEATURE_LABELS.get(name, name),
            psi=round(psi, 4),
            status=feature_status,
        ))

    features.sort(key=lambda f: f.psi, reverse=True)
    return DriftReport(
        model_version=predictor.version,
        samples_analyzed=len(snapshots),
        features=features,
        overall_status=worst,
    )
