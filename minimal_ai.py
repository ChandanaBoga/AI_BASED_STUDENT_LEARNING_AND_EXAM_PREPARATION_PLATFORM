from fastapi import FastAPI
import uvicorn
import ollama
app = FastAPI()
@app.get("/")
def h(): return {"ok": True}
if __name__ == "__main__":
    print("Starting minimal AI with ollama import...")
    uvicorn.run(app, host="127.0.0.1", port=8001)
