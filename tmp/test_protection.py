import requests
import json
import os

URL = "http://127.0.0.1:8001/save_user"
USER_FILE = r"c:\Program Files\webapp\data\users\boga_chandana.json"

# 1. Read current note content
with open(USER_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)
    original_notes_count = len(data.get('notes', []))
    print(f"Original notes count: {original_notes_count}")

if original_notes_count == 0:
    print("Error: No notes found in file to test against.")
    exit(1)

# 2. Simulate a "bad sync" from frontend (empty notes)
payload = {
    "fullname": "BOGA CHANDANA",
    "notes": []  # This should be REJECTED/MERGED by the backend
}

print("Sending 'bad' sync request with empty notes...")
response = requests.post(URL, json=payload)
print(f"Server response: {response.status_code} - {response.json()}")

# 3. Verify if notes were preserved
with open(USER_FILE, 'r', encoding='utf-8') as f:
    new_data = json.load(f)
    new_notes_count = len(new_data.get('notes', []))
    print(f"New notes count after 'bad' sync: {new_notes_count}")

if new_notes_count == original_notes_count:
    print("SUCCESS: Backend successfully protected and preserved the notes!")
else:
    print("FAILURE: Notes were deleted by the empty sync request.")
