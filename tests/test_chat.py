import requests
import json

url = "http://localhost:8001/chat"
data = {"message": "Who is the principal of TKR College?"}

try:
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json().get('response')}")
except Exception as e:
    print(f"Error: {e}")
