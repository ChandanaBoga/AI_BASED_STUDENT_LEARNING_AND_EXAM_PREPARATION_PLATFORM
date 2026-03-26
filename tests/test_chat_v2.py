import requests
import json
import sys

url = "http://localhost:8001/chat"
data = {"message": "Who is the principal of TKR College?"}

print(f"Sending request to {url}...")
try:
    response = requests.post(url, json=data, timeout=60)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {result.get('response')}")
    else:
        print(f"Error: {response.text}")
except requests.exceptions.Timeout:
    print("Error: Request timed out after 60 seconds")
except Exception as e:
    print(f"Error: {e}")
sys.exit(0)
