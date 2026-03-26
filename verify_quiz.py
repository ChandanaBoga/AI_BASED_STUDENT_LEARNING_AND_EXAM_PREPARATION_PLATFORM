
import requests
import json
import time

def test_quiz_generation():
    url = "http://localhost:8001/generate_quiz"
    payload = {
        "topic": "SOFTWARE ENGINEERING",
        "difficulty": "moderate",
        "num_questions": 2
    }
    
    print(f"Testing {url} with topic: {payload['topic']}...")
    try:
        # Increased timeout to 180s to match backend
        response = requests.post(url, json=payload, timeout=180)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "quiz" in data:
                print("SUCCESS: Quiz generated and parsed correctly.")
                print(json.dumps(data["quiz"], indent=2))
            elif "error" in data:
                print(f"FAILED: Backend reported error: {data['error']}")
                if "raw" in data:
                    print(f"Raw response was: {data['raw']}")
            else:
                print(f"FAILED: Unexpected response format: {data}")
        else:
            print(f"FAILED: Server returned {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    # Give the server a few seconds to fully initialize
    time.sleep(5)
    test_quiz_generation()
