from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from app.database import Base, engine, get_db
from app.schemas import TrainRequest, ScoreRequest, ScoreResponse, AlertResponse
from app.services.feature_builder import build_training_dataframe, feature_vector_from_payload
from app.services.ai_model import AIModelService
from app import models

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SCADA AI Module",
    description="Интеллектуальный аналитический модуль на базе open-source IsolationForest",
    version="1.0.0",
)

ai_service = AIModelService()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ai/train")
def train_model(req: TrainRequest, db: Session = Depends(get_db)):
    df = build_training_dataframe(db, req.metric_names)
    if df.empty or len(df) < req.min_complete_rows:
        raise HTTPException(
            status_code=400,
            detail=f"Недостаточно полных строк для обучения. Получено: {len(df)}"
        )

    ai_service.train(df, req.metric_names, contamination=req.contamination)
    return {
        "status": "trained",
        "rows_used": int(len(df)),
        "metric_names": req.metric_names,
        "model_path": str(ai_service.model_path),
    }


@app.post("/ai/score", response_model=ScoreResponse)
def score(req: ScoreRequest):
    try:
        bundle = ai_service.load()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    metric_names = bundle["metric_names"]
    x = feature_vector_from_payload(req.features, metric_names)
    result = ai_service.score(x)
    return ScoreResponse(
        device_name=req.device_name,
        anomaly_score=result["anomaly_score"],
        is_anomaly=result["is_anomaly"],
        used_features={m: float(x.iloc[0][m]) for m in metric_names},
    )


@app.post("/ai/score-and-alert", response_model=AlertResponse)
def score_and_alert(req: ScoreRequest, db: Session = Depends(get_db)):
    try:
        bundle = ai_service.load()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    metric_names = bundle["metric_names"]
    x = feature_vector_from_payload(req.features, metric_names)
    result = ai_service.score(x)

    device = db.query(models.Device).filter(models.Device.name == req.device_name).first()
    if not device:
        raise HTTPException(status_code=404, detail=f"Устройство {req.device_name} не найдено в БД")

    alert_created = False
    message = "Аномалия не обнаружена"
    if result["is_anomaly"]:
        message = f"Обнаружена аномалия. Score={result['anomaly_score']}"
        db.add(
            models.Alert(
                device_id=device.id,
                metric_name="ai_anomaly_score",
                metric_value=result["anomaly_score"],
                severity="high",
                message=message,
            )
        )
        db.commit()
        alert_created = True

    return AlertResponse(
        device_name=req.device_name,
        anomaly_score=result["anomaly_score"],
        is_anomaly=result["is_anomaly"],
        alert_created=alert_created,
        message=message,
    )
