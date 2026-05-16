import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

KB_PATH = Path(__file__).resolve().parents[1] / "kb" / "knowledge_base.json"

COMMON_TERMS = {
    "用户",
    "客服",
    "问题",
    "处理",
    "反馈",
    "当前",
    "已经",
    "没有",
    "需要",
    "进行",
    "确认",
    "方案",
    "投诉",
    "补偿",
    "赔付",
    "核实",
    "人工",
    "不满",
    "焦虑",
    "着急",
}

DOMAIN_TERMS = [
    "航班",
    "延误",
    "取消",
    "改签",
    "酒店",
    "订单",
    "无房",
    "入住",
    "外卖",
    "配送",
    "超时",
    "商品",
    "破损",
    "退款",
    "到账",
    "优惠券",
    "承诺",
    "回复",
    "回电",
    "主管",
    "升级",
    "情绪",
    "售后",
    "凭证",
]


@lru_cache
def load_knowledge_base() -> list[dict[str, Any]]:
    with KB_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def _flatten_value(value: Any) -> str:
    if isinstance(value, list):
        return " ".join(_flatten_value(item) for item in value)
    if isinstance(value, dict):
        return " ".join(_flatten_value(item) for item in value.values())
    return str(value)


def knowledge_to_text(item: dict[str, Any]) -> str:
    fields = [
        item.get("title", ""),
        item.get("category", ""),
        item.get("keywords", []),
        item.get("scenario", ""),
        item.get("typical_causes", []),
        item.get("conditions", []),
        item.get("required_checks", []),
        item.get("resolution_steps", []),
        item.get("compensation_policy", {}),
        item.get("suggested_actions", []),
        item.get("suggested_script", ""),
        item.get("risk_note", ""),
    ]
    return " ".join(_flatten_value(field) for field in fields)


def _tokenize(text: str) -> set[str]:
    normalized = text.lower()
    tokens = set(re.findall(r"[a-z0-9]+|[\u4e00-\u9fff]{2,}", normalized))

    for term in DOMAIN_TERMS:
        if term in text:
            tokens.add(term)

    return {token for token in tokens if token not in COMMON_TERMS}


def _keyword_score(query: str, document: str) -> float:
    query_tokens = _tokenize(query)
    document_tokens = _tokenize(document)

    if not query_tokens or not document_tokens:
        return 0.0

    overlap = query_tokens & document_tokens
    coverage = len(overlap) / len(query_tokens)
    density = len(overlap) / len(document_tokens)
    domain_bonus = sum(0.08 for term in DOMAIN_TERMS if term in overlap)

    return round(coverage * 0.7 + density * 0.3 + domain_bonus, 4)


def _explicit_keyword_score(query: str, item: dict[str, Any]) -> float:
    keywords = item.get("keywords", [])
    if not keywords:
        return 0.0

    matched = [keyword for keyword in keywords if str(keyword).lower() in query.lower()]
    return len(matched) / len(keywords)


def search_knowledge(query: str, top_k: int = 3) -> list[dict[str, Any]]:
    scored_items = []

    for item in load_knowledge_base():
        keyword_score = _explicit_keyword_score(query, item)
        text_score = _keyword_score(query, knowledge_to_text(item))
        score = round(keyword_score * 0.7 + text_score * 0.3, 4)
        scored_items.append({**item, "score": score})

    scored_items.sort(key=lambda item: item["score"], reverse=True)
    return scored_items[:top_k]
