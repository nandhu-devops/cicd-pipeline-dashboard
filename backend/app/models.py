from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from .db import Base

class Provider(Base):
    """CI/CD tool provider (GitHub Actions, etc.)"""
    __tablename__ = "providers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    kind = Column(String, nullable=False)  # github_actions, gitlab, etc.
    config_json = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    builds = relationship("Build", back_populates="provider")

class Build(Base):
    """Individual CI/CD build/pipeline execution"""
    __tablename__ = "builds"
    
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, nullable=False, index=True)  # Build ID from provider
    status = Column(String, nullable=False, index=True)  # success, failed, running, queued, etc.
    branch = Column(String, nullable=True, index=True)
    commit_sha = Column(String, nullable=True)
    triggered_by = Column(String, nullable=True)
    url = Column(String, nullable=True)  # Link to build in provider
    
    # Timing
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Float, nullable=True)
    
    # Provider relationship
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    provider = relationship("Provider", back_populates="builds")
    
    # Raw data and metadata
    raw_payload = Column(JSON, nullable=True)  # Original webhook payload
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Alert(Base):
    """Alert configuration and history"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)  # email, slack, webhook
    name = Column(String, nullable=False)
    config_json = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class AlertHistory(Base):
    """History of sent alerts"""
    __tablename__ = "alert_history"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=False)
    build_id = Column(Integer, ForeignKey("builds.id"), nullable=True)
    message = Column(Text, nullable=False)
    severity = Column(String, nullable=False)  # info, warning, error, critical
    status = Column(String, nullable=False)  # sent, failed, pending
    error_message = Column(Text, nullable=True)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    alert = relationship("Alert")
    build = relationship("Build")

class Settings(Base):
    """Application settings and configuration"""
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False, index=True)
    value = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Metrics(Base):
    """Aggregated metrics for dashboard"""
    __tablename__ = "metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String, nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String, nullable=True)
    window_start = Column(DateTime(timezone=True), nullable=False)
    window_end = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    class Meta:
        indexes = [
            ("metric_name", "window_start", "window_end")
        ]
