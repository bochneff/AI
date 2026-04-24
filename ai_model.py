from __future__ import annotations
from pathlib import Path
import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest
from app.config import settings


class AIModelService:
    def __init__(self, model_path: str | None = None):
        self.model_path = Path(model_path or settings.model_path)

    def save(self, bundle: dict):
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(bundle, self.model_path)

    def load(self) -> dict:
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
        return joblib.load(self.model_path)

    def train(self, df: pd.DataFrame, metric_names: list[str], contamination: float = 0.05):
        x = df[metric_names].copy()
        model = IsolationForest(
            n_estimators=200,
            contamination=contamination,
            random_state=42,
        )
        model.fit(x)

        bundle = {
            "model": model,
            "metric_names": metric_names,
            "threshold": settings.anomaly_threshold,
        }
        self.save(bundle)
        return bundle

    def score(self, x: pd.DataFrame) -> dict:
        bundle = self.load()
        model = bundle["model"]
        metric_names = bundle["metric_names"]
        threshold = bundle["threshold"]

        xx = x[metric_names].copy()
        # В sklearn decision_function: чем меньше, тем более аномально.
        raw_score = model.decision_function(xx)[0]
        # Приводим к удобной шкале "чем больше, тем хуже"
        anomaly_score = round(max(0.0, min(1.0, 0.5 - raw_score)), 4)
        is_anomaly = anomaly_score >= threshold

        return {
            "anomaly_score": anomaly_score,
            "is_anomaly": bool(is_anomaly),
            "metric_names": metric_names,
            "threshold": threshold,
        }
