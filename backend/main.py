from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.recommend import router as recommend_router
from app.api.summary import router as summary_router

app = FastAPI(title="AI Customer Service Copilot MVP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(summary_router)
app.include_router(recommend_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
