"use client";

import { MessagesSquare } from "lucide-react";
import type { RecommendationResponse, SummaryResult } from "@/lib/api";
import { CopyButton } from "./CopyButton";

type RecommendationPanelProps = {
  currentIssue: string;
  summary: SummaryResult | null;
  result: RecommendationResponse | null;
  isLoading: boolean;
  onIssueChange: (value: string) => void;
  onRecommend: () => void;
};

export function RecommendationPanel({
  currentIssue,
  summary,
  result,
  isLoading,
  onIssueChange,
  onRecommend
}: RecommendationPanelProps) {
  const copyText = result
    ? [
        "推荐方案：",
        ...result.recommendation.suggested_actions.map((item) => `- ${item}`),
        "",
        "推荐话术：",
        result.recommendation.suggested_script,
        "",
        "风险提醒：",
        result.recommendation.risk_note
      ].join("\n")
    : "";

  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">AI Recommendation</p>
          <h2>处理方案与话术</h2>
        </div>
        <CopyButton text={copyText} disabled={!result} />
      </div>

      <textarea
        className="textarea small"
        value={currentIssue}
        onChange={(event) => onIssueChange(event.target.value)}
        placeholder="输入当前用户问题，例如：用户继续投诉航班延误，希望获得补偿..."
      />

      <button
        className="primary-button"
        type="button"
        onClick={onRecommend}
        disabled={
          isLoading || !summary || currentIssue.trim().length === 0
        }
      >
        <MessagesSquare size={18} />
        <span>{isLoading ? "检索中" : "获取推荐方案"}</span>
      </button>

      {result ? (
        <div className="recommendation">
          <div>
            <h3>推荐方案</h3>
            <ul>
              {result.recommendation.suggested_actions.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>

          <div>
            <h3>推荐话术</h3>
            <p>{result.recommendation.suggested_script}</p>
          </div>

          <div>
            <h3>风险提醒</h3>
            <p>{result.recommendation.risk_note}</p>
          </div>
        </div>
      ) : (
        <div className="empty-state">
          生成总结后输入当前问题，即可检索知识库并推荐处理方案。
        </div>
      )}
    </section>
  );
}

