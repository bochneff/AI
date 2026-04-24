import requests

BASE_URL = "http://127.0.0.1:8000"

resp = requests.post(
    f"{BASE_URL}/ai/score-and-alert",
    json={
        "device_name": "SNR-SW-01",
        "features": {
            "cpu": 91,
            "temperature": 78,
            "packet_loss": 8,
            "channel_utilization": 89,
            "crc_errors": 12
        }
    },
    timeout=30,
)
print(resp.status_code, resp.json())
