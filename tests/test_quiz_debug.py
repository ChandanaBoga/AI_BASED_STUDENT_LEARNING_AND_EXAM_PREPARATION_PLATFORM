import requests
import json

url = "http://localhost:8001/generate_quiz"
data = {"topic": "Python Functions", "num_questions": 2}

try:
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response Body: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
