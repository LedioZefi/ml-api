"""Demo script to test the /predict endpoint."""
import requests

payload = {
    "sepal_length": 5.1,
    "sepal_width": 3.5,
    "petal_length": 1.4,
    "petal_width": 0.2,
}
r = requests.post("http://127.0.0.1:8000/predict", json=payload, timeout=10)
print(r.status_code, r.json())
