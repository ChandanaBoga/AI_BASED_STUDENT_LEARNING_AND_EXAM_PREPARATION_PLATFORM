import asyncio
import os
from ollama import Client

# Test the new standardized host format
HOST = "http://127.0.0.1:11434"
print(f"Testing connectivity to: {HOST}")

async def test_robust_client():
    client = Client(host=HOST)
    try:
        print("Calling Ollama...")
        response = await asyncio.to_thread(
            client.chat,
            model='llama3.2:3b',
            messages=[{'role': 'user', 'content': 'Say hello!'}]
        )
        print("SUCCESS! Ollama responded.")
        print("Response:", response['message']['content'])
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(test_robust_client())
