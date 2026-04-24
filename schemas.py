from typing import Optional
from pydantic import BaseModel, Field


class TrainRequest(BaseModel):
    metric_names: list[str] = Field(
        default=["cpu", "temperature", "packet_loss", "channel_utilization", "crc_errors"]
    )
    min_complete_rows: int = 100
    contamination: float = 0.05


class ScoreRequest(BaseModel):
    device_name: str
    features: dict[str, float]


class ScoreResponse(BaseModel):
    device_name: str
    anomaly_score: float
    is_anomaly: bool
    used_features: dict[str, float]


class AlertResponse(BaseModel):
    device_name: str
    anomaly_score: float
    is_anomaly: bool
    alert_created: bool
    message: str
