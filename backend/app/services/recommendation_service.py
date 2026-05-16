import json
from typing import Any

from app.core.config import get_settings
from app.core.llm import get_llm_client
from app.schemas.recommend import (
    MatchedKnowledge,
    RecommendationResult,
    RecommendResponse,
)
from app.schemas.summary import SummaryResult
from app.services.knowledge_service import search_knowledge


SYSTEM_PROMPT = """
你是 AI 客服辅助 Copilot，只给人工客服提供处理建议。

要求：
1. 只能基于当前用户问题、AI 总结和知识库案例生成建议。
2. 不自动决策，不自动赔付，不承诺一定退款、一定补偿或一定升级成功。
3. 推荐方案必须具体、可执行，优先引用知识库中的事故原因、核查项、处理步骤和补偿规则。
4. 避免使用知识库 forbidden_script 中的表达。
5. 如果涉及补偿金额，只能写成“建议人工评估/可建议”，不能写成“已发放/一定发放”。
6. 推荐话术必须是客服可直接参考的温和表达。
7. 只输出 JSON，不要输出 Markdown，不要输出解释。
8. 禁止照抄字段说明，禁止输出“核查项：需要客服先确认的信息”“推荐客服话术”“风险提醒”等占位文本。

JSON 字段必须为：
{
  "suggested_actions": ["具体动作1", "具体动作2", "具体动作3"],
  "suggested_script": "完整的客服话术，不要使用省略号",
  "risk_note": "具体风险提醒"
}
""".strip()


def _summary_to_query(summary: SummaryResult) -> str:
    return " ".join(
        [
            summary.user_issue,
            summary.progress,
            summary.emotion,
            summary.compensation,
            summary.pending_items,
        ]
    )


def _build_user_prompt(
    current_issue: str,
    summary: SummaryResult,
    matched_items: list[dict[str, Any]],
) -> str:
    knowledge_text = json.dumps(matched_items, ensure_ascii=False, indent=2)

    return f"""
当前用户问题：
{current_issue}

AI 总结：
用户遇到的问题：{summary.user_issue}
当前处理进度：{summary.progress}
用户情绪状态：{summary.emotion}
是否已有补偿：{summary.compensation}
当前待解决事项：{summary.pending_items}

检索到的知识库案例：
{knowledge_text}
""".strip()


def _clean_json_content(content: str) -> str:
    cleaned = content.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.startswith("json"):
            cleaned = cleaned[4:].strip()

    return cleaned


def _fallback_recommendation(matched_items: list[dict[str, Any]]) -> RecommendationResult:
    if not matched_items:
        return RecommendationResult(
            suggested_actions=["升级人工客服进一步核实用户诉求"],
            suggested_script="非常理解您的心情，我们会先核实您反馈的问题，并根据平台规则协助确认下一步处理方式。",
            risk_note="该建议仅供人工客服参考，具体处理方案需按业务规则确认。",
        )

    primary = matched_items[0]
    required_checks = primary.get("required_checks", [])[:2]
    resolution_steps = primary.get("resolution_steps", [])[:3]
    compensation = primary.get("compensation_policy", {})
    compensation_action = ""

    if compensation:
        compensation_action = (
            f"补偿建议：{compensation.get('amount', '按规则评估')}；"
            f"{compensation.get('notes', '需人工确认。')}"
        )

    actions = [
        *(f"核查项：{item}" for item in required_checks),
        *(f"处理步骤：{item}" for item in resolution_steps),
    ]

    if compensation_action:
        actions.append(compensation_action)

    return RecommendationResult(
        suggested_actions=actions[:6],
        suggested_script=primary.get("suggested_script", ""),
        risk_note=primary.get("risk_note", "具体处理方案需由人工客服按规则确认。"),
    )


def _is_placeholder_result(result: RecommendationResult) -> bool:
    placeholder_terms = [
        "需要客服先确认的信息",
        "可执行的处理动作",
        "可建议的金额或券",
        "推荐客服话术",
        "风险提醒",
        "具体动作",
        "不要使用省略号",
        "...",
        "……",
    ]
    text = " ".join(
        [
            *result.suggested_actions,
            result.suggested_script,
            result.risk_note,
        ]
    )
    return any(term in text for term in placeholder_terms)


def _parse_recommendation(
    content: str,
    matched_items: list[dict[str, Any]],
) -> RecommendationResult:
    try:
        data = json.loads(_clean_json_content(content))
        result = RecommendationResult(**data)
        if _is_placeholder_result(result):
            return _fallback_recommendation(matched_items)
        return result
    except Exception:
        return _fallback_recommendation(matched_items)


def generate_recommendation(
    current_issue: str,
    summary: SummaryResult,
    top_k: int = 3,
) -> RecommendResponse:
    settings = get_settings()
    client = get_llm_client()
    query = f"{current_issue} {_summary_to_query(summary)}"
    matched_items = search_knowledge(query, top_k=top_k)

    completion = client.chat.completions.create(
        model=settings.summary_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": _build_user_prompt(current_issue, summary, matched_items),
            },
        ],
        temperature=0.2,
    )

    content = completion.choices[0].message.content or "{}"
    recommendation = _parse_recommendation(content, matched_items)
    matched_knowledge = [
        MatchedKnowledge(
            title=item["title"],
            category=item["category"],
            score=item["score"],
        )
        for item in matched_items
    ]

    return RecommendResponse(
        matched_knowledge=matched_knowledge,
        recommendation=recommendation,
    )
