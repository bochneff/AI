import requests

BASE_URL = "http://127.0.0.1:8000"

resp = requests.post(
    f"{BASE_URL}/ai/train",
    json={
        "metric_names": ["cpu", "temperature", "packet_loss", "channel_utilization", "crc_errors"],
        "min_complete_rows": 10,
        "contamination": 0.05,
    },
    timeout=60,
)
print(resp.status_code, resp.json())
