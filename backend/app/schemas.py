from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# Enums
class BuildStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    RUNNING = "running"
    QUEUED = "queued"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"

class AlertType(str, Enum):
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"

class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

# Base Models
class Provider(BaseModel):
    id: int
    name: str
    kind: str
    config_json: Optional[Dict[str, Any]] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class Build(BaseModel):
    id: int
    external_id: str
    status: str
    branch: Optional[str] = None
    commit_sha: Optional[str] = None
    triggered_by: Optional[str] = None
    url: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    provider_name: Optional[str] = None

class Alert(BaseModel):
    id: int
    type: str
    name: str
    config_json: Dict[str, Any]
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class AlertHistory(BaseModel):
    id: int
    alert_id: int
    build_id: Optional[int] = None
    message: str
    severity: str
    status: str
    error_message: Optional[str] = None
    sent_at: Optional[datetime] = None

class Settings(BaseModel):
    id: int
    key: str
    value: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class Metrics(BaseModel):
    id: int
    metric_name: str
    metric_value: float
    metric_unit: Optional[str] = None
    window_start: datetime
    window_end: datetime
    created_at: Optional[datetime] = None

# Response Models
class MetricsSummary(BaseModel):
    window_days: int
    success_rate: float
    failure_rate: float
    avg_build_time_seconds: float
    last_build_status: str
    last_updated: datetime

class BuildListResponse(BaseModel):
    builds: List[Build]
    total: int
    limit: int
    offset: int

class HealthResponse(BaseModel):
    ok: bool
    timestamp: datetime
    version: str
    database: str

# Webhook Payloads
class GitHubWebhookPayload(BaseModel):
    action: str
    run_id: int
    repository: Dict[str, Any]
    head_branch: str
    head_sha: str
    actor: Dict[str, Any]
    html_url: str
    run_started_at: datetime
    updated_at: datetime
    conclusion: Optional[str] = None



# Alert Models
class AlertTestRequest(BaseModel):
    message: str
    severity: str = "info"
    alert_type: str = "email"

class AlertTestResponse(BaseModel):
    success: bool
    message: str

# Seed Models
class SeedRequest(BaseModel):
    pass

class SeedResponse(BaseModel):
    success: bool
    message: str
    builds_created: int
    providers_created: int
