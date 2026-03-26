import requests
import json

BASE_URL = "http://localhost:8001"

def test_save():
    profile = {
        "fullname": "Test User",
        "age": "20",
        "dob": "2004-01-01",
        "year": "2",
        "semester": "4",
        "roll": "12345"
    }
    resp = requests.post(f"{BASE_URL}/save_user", json=profile)
    print(f"Save Response: {resp.status_code} - {resp.text}")

def test_load():
    resp = requests.get(f"{BASE_URL}/load_user/Test%20User")
    print(f"Load Response: {resp.status_code} - {resp.text}")

if __name__ == "__main__":
    test_save()
    test_load()
