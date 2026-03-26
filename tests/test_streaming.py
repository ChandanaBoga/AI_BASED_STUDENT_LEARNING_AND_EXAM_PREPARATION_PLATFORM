import requests
import json

url = "http://localhost:8001/chat/stream"
data = {"message": "Hello, who are you?"}

try:
    response = requests.post(url, json=data, stream=True)
    print(f"Status: {response.status_code}")
    for line in response.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')
            if decoded_line.startswith("data: "):
                payload = decoded_line[6:]
                if payload == "[DONE]":
                    print("\n[DONE]")
                    break
                try:
                    obj = json.loads(payload)
                    if "token" in obj:
                        print(obj["token"], end="", flush=True)
                except:
                    pass
except Exception as e:
    print(f"Error: {e}")
