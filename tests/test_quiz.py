import requests
import json

url = "http://localhost:8001/generate_quiz"
data = {"topic": "Python Functions", "num_questions": 2}

try:
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        quiz = response.json().get("quiz", [])
        print(f"Quiz count: {len(quiz)}")
        for i, q in enumerate(quiz):
            print(f"Q{i+1}: {q['question']}")
    else:
        print(f"Error response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
