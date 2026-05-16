from pydantic import BaseModel, Field

from app.schemas.summary import SummaryResult


class RecommendRequest(BaseModel):
    current_issue: str = Field(..., min_length=1)
    summary: SummaryResult


class MatchedKnowledge(BaseModel):
    title: str
    category: str
    score: float


class RecommendationResult(BaseModel):
    suggested_actions: list[str]
    suggested_script: str
    risk_note: str


class RecommendResponse(BaseModel):
    matched_knowledge: list[MatchedKnowledge]
    recommendation: RecommendationResult

