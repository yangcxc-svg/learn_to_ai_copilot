from fastapi import APIRouter, HTTPException

from app.schemas.summary import SummaryRequest, SummaryResponse
from app.services.summary_service import generate_summary

router = APIRouter(prefix="/api", tags=["summary"])


@router.post("/summary", response_model=SummaryResponse)
def create_summary(payload: SummaryRequest) -> SummaryResponse:
    chat_history = payload.chat_history.strip()

    if not chat_history:
        raise HTTPException(status_code=400, detail="chat_history 不能为空")

    try:
        return generate_summary(chat_history)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"生成总结失败：{exc}") from exc

