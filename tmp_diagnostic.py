import ollama
import os
import asyncio

# Match launcher_app.py environment
os.environ["OLLAMA_HOST"] = "127.0.0.1:11434"

async def test_quiz():
    system_prompt = "You are a strict JSON-only quiz generation engine for TKRCET."
    prompt = "Generate a moderate difficulty quiz about 'PYTHON' with exactly 1 questions."
    
    print(f"Using OLLAMA_HOST: {os.getenv('OLLAMA_HOST')}")
    print("Calling Ollama...")
    
    try:
        response = await asyncio.to_thread(
            ollama.chat,
            model='llama3.2:3b',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user',   'content': prompt},
            ]
        )
        print("Ollama responded successfully!")
        print("Content:", response['message']['content'])
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(test_quiz())
