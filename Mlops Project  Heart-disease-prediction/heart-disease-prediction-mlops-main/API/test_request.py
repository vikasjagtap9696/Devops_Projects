import requests

BASE_URL = "http://127.0.0.1:8000"

# Test health
print(requests.get(f"{BASE_URL}/health").json())

# Test predict
patient = {
    "age": 85,
    "sex": 1,
    "cp": 0,
    "trestbps": 160,
    "chol": 289,
    "fbs": 1,
    "restecg": 0,
    "thalach": 145,
    "exang": 0,
    "oldpeak": 2.8,
    "slope": 0,
    "ca": 0,
    "thal": 1
}

response = requests.post(f"{BASE_URL}/predict", json=patient)
print(response.status_code)
print(response.json())