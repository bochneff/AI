# Интеллектуальный аналитический модуль

Open-source AI модуль для поиска аномалий в телеметрии и сетевой статистике.

## Что делает
- читает метрики из SQL-базы;
- формирует обучающую выборку по устройствам и временным срезам;
- обучает модель `IsolationForest`;
- сохраняет модель в файл;
- рассчитывает anomaly score для новых данных;
- создаёт тревоги, если аномалия превышает порог.

## Почему выбрана именно эта модель
`IsolationForest` из scikit-learn подходит для поиска аномалий без большого размеченного датасета.
Официальная документация sklearn описывает её как метод outlier/anomaly detection на основе случайных разбиений признаков.

## Быстрый запуск
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Инициализация БД из вашего серверного модуля должна быть уже выполнена
uvicorn app.main:app --reload
```

## Основные API
- `POST /ai/train` — обучение модели по данным из SQL-базы
- `POST /ai/score` — расчёт anomaly score по одному срезу метрик
- `POST /ai/score-and-alert` — расчёт score + решение, нужно ли открыть тревогу

## Пример score-запроса
```bash
curl -X POST http://127.0.0.1:8000/ai/score \
  -H "Content-Type: application/json" \
  -d '{
    "device_name": "SNR-SW-01",
    "features": {
      "cpu": 91,
      "temperature": 78,
      "packet_loss": 8,
      "channel_utilization": 89,
      "crc_errors": 12
    }
  }'
```
