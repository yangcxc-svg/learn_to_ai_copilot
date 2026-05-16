export type SummaryResult = {
  user_issue: string;
  progress: string;
  emotion: string;
  compensation: string;
  pending_items: string;
};

export type SummaryResponse = {
  summary: SummaryResult;
  raw_text: string;
};

export type RecommendationResponse = {
  matched_knowledge: Array<{
    title: string;
    category: string;
    score?: number;
  }>;
  recommendation: {
    suggested_actions: string[];
    suggested_script: string;
    risk_note: string;
  };
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

async function request<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(body)
  });

  if (!response.ok) {
    throw new Error(`请求失败：${response.status}`);
  }

  return response.json() as Promise<T>;
}

export function generateSummary(chatHistory: string) {
  return request<SummaryResponse>("/api/summary", {
    chat_history: chatHistory
  });
}

export function getRecommendation(
  currentIssue: string,
  summary: SummaryResult
) {
  return request<RecommendationResponse>("/api/recommend", {
    current_issue: currentIssue,
    summary
  });
}

