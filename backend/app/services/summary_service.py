import json

from app.core.config import get_settings
from app.core.llm import get_llm_client
from app.schemas.summary import SummaryResult, SummaryResponse


SYSTEM_PROMPT = """
你是一个 AI 客诉辅助 Copilot，只帮助人工客服理解历史沟通内容。

请根据用户提供的历史客服聊天记录，提取结构化摘要。
要求：
1. 不要编造聊天记录中没有的信息。
2. 如果某项信息不存在，请填写“未提及”。
3. 不要给出处理决策，不要承诺补偿。
4. 只输出 JSON，不要输出 Markdown，不要输出解释。
5. “是否已有补偿”字段要判断补偿状态，优先使用“已有补偿”“尚未提供补偿”“补偿方案待确认”“未提及”等明确表达。

JSON 字段必须为：
{
  "user_issue": "用户遇到的问题",
  "progress": "当前处理进度",
  "emotion": "用户情绪状态",
  "compensation": "是否已有补偿",
  "pending_items": "当前待解决事项"
}
""".strip()


def _build_user_prompt(chat_history: str) -> str:
    return f"""
请总结以下历史客服聊天记录：

{chat_history}
""".strip()


def _parse_summary(content: str) -> SummaryResult:
    cleaned = content.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.startswith("json"):
            cleaned = cleaned[4:].strip()

    data = json.loads(cleaned)
    return SummaryResult(**data)


def generate_summary(chat_history: str) -> SummaryResponse:
    settings = get_settings()
    client = get_llm_client()

    completion = client.chat.completions.create(
        model=settings.summary_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_prompt(chat_history)},
        ],
        temperature=0.2,
    )

    content = completion.choices[0].message.content or "{}"
    summary = _parse_summary(content)
    raw_text = "；".join(
        [
            summary.user_issue,
            summary.progress,
            summary.emotion,
            summary.compensation,
            summary.pending_items,
        ]
    )

    return SummaryResponse(summary=summary, raw_text=raw_text)
