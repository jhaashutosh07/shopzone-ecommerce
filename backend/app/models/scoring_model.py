from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, LargeBinary, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class ScoringModel(Base):
    __tablename__ = "scoring_models"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    merchant_id = Column(String(36), ForeignKey("merchants.id"), nullable=True, index=True)  # NULL = global model

    version = Column(Integer, nullable=False, default=1)
    model_type = Column(String(50), default="gradient_boosting")  # Type of ML model

    # Model binary (serialized with joblib)
    model_blob = Column(LargeBinary, nullable=True)

    # Model metadata
    features_used = Column(String(1000), nullable=True)  # JSON array of feature names
    training_samples = Column(Integer, default=0)
    accuracy = Column(Float, nullable=True)
    precision_score = Column(Float, nullable=True)
    recall_score = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)

    # Status
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    trained_at = Column(DateTime, nullable=True)

    # Relationships
    merchant = relationship("Merchant", back_populates="scoring_models")

    def __repr__(self):
        scope = f"merchant_{self.merchant_id[:8]}" if self.merchant_id else "global"
        return f"<ScoringModel v{self.version} ({scope})>"
