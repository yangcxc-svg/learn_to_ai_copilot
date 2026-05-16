from fastapi import APIRouter, HTTPException

from app.schemas.recommend import RecommendRequest, RecommendResponse
from app.services.recommendation_service import generate_recommendation

router = APIRouter(prefix="/api", tags=["recommend"])


@router.post("/recommend", response_model=RecommendResponse)
def create_recommendation(payload: RecommendRequest) -> RecommendResponse:
    current_issue = payload.current_issue.strip()

    if not current_issue:
        raise HTTPException(status_code=400, detail="current_issue 不能为空")

    try:
        return generate_recommendation(current_issue, payload.summary)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"生成推荐方案失败：{exc}") from exc

