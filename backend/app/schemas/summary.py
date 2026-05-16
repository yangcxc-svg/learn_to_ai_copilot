from pydantic import BaseModel, Field


class SummaryRequest(BaseModel):
    chat_history: str = Field(..., min_length=1)


class SummaryResult(BaseModel):
    user_issue: str
    progress: str
    emotion: str
    compensation: str
    pending_items: str


class SummaryResponse(BaseModel):
    summary: SummaryResult
    raw_text: str

