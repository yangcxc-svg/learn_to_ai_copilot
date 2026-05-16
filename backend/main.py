from fastapi import FastAPI

app = FastAPI(title="AI Customer Service Copilot MVP")


@app.get("/health")
def health_check():
    return {"status": "ok"}

