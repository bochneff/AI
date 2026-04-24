from __future__ import annotations
import pandas as pd
from sqlalchemy.orm import Session
from app import models
from app.config import settings


def build_training_dataframe(db: Session, metric_names: list[str]) -> pd.DataFrame:
    '''
    Формирует обучающую выборку из таблицы metrics.
    Одна строка = один временной срез устройства.
    Для простоты берём округление времени до минуты.
    '''
    rows = (
        db.query(
            models.Device.name.label("device_name"),
            models.Metric.metric_name,
            models.Metric.metric_value,
            models.Metric.timestamp,
        )
        .join(models.Device, models.Device.id == models.Metric.device_id)
        .order_by(models.Metric.timestamp.desc())
        .limit(settings.training_limit_rows)
        .all()
    )

    if not rows:
        return pd.DataFrame()

    raw = pd.DataFrame(
        [
            {
                "device_name": r.device_name,
                "metric_name": r.metric_name,
                "metric_value": r.metric_value,
                "timestamp": r.timestamp,
            }
            for r in rows
        ]
    )

    raw = raw[raw["metric_name"].isin(metric_names)].copy()
    if raw.empty:
        return pd.DataFrame()

    raw["ts_bucket"] = pd.to_datetime(raw["timestamp"]).dt.floor("min")
    pivot = raw.pivot_table(
        index=["device_name", "ts_bucket"],
        columns="metric_name",
        values="metric_value",
        aggfunc="mean",
    ).reset_index()

    # Оставляем только строки, где есть все нужные метрики
    pivot = pivot.dropna(subset=metric_names, how="any")
    return pivot


def feature_vector_from_payload(features: dict[str, float], metric_names: list[str]) -> pd.DataFrame:
    row = {}
    for m in metric_names:
        row[m] = float(features.get(m, 0.0))
    return pd.DataFrame([row])
