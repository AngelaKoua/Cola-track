from sqlalchemy import Column, String, Float, DateTime, Boolean, Integer, func
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.database import Base

class Prediction(Base):
    """
    ML Predictions Data Model.
    
    Stores the results of the Hybrid Inference Engine for each machine.
    Used by the dashboard to instantly fetch the latest AI insights.
    
    Table: predictions
    """
    __tablename__ = "predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    timestamp = Column(DateTime(timezone=True), default=func.now(), nullable=False, index=True)
    machine_id = Column(String(50), nullable=False, index=True)
    
    # ML Metrics
    health_index = Column(Float, nullable=False)
    failure_probability_24h = Column(Float, nullable=False)
    quality_risk = Column(Float, nullable=True) # Applicable mainly for Remplisseuse
    is_anomaly = Column(Boolean, nullable=False, default=False)
    
    # Hybrid Engine Output
    alert_level = Column(Integer, nullable=False, default=0) # 0: Normal, 1: Warning, 2: Critical, 3: Halt
    reason = Column(String(500), nullable=True) # Serialized list of reasons or main reason

    def __repr__(self):
        return f"<Prediction(machine_id={self.machine_id}, level={self.alert_level}, prob={self.failure_probability_24h})>"
