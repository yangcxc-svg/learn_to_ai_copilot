"use client";

import { useMemo, useState } from "react";
import { ChatInputPanel } from "@/components/ChatInputPanel";
import { RecommendationPanel } from "@/components/RecommendationPanel";
import { SummaryPanel } from "@/components/SummaryPanel";
import {
  generateSummary,
  getRecommendation,
  type RecommendationResponse,
  type SummaryResult
} from "@/lib/api";

export default function Home() {
  const [chatHistory, setChatHistory] = useState("");
  const [currentIssue, setCurrentIssue] = useState("");
  const [summary, setSummary] = useState<SummaryResult | null>(null);
  const [summaryRawText, setSummaryRawText] = useState("");
  const [recommendation, setRecommendation] =
    useState<RecommendationResponse | null>(null);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [recommendationLoading, setRecommendationLoading] = useState(false);
  const [error, setError] = useState("");

  const statusText = useMemo(() => {
    if (summaryLoading) {
      return "正在生成历史记录总结";
    }

    if (recommendationLoading) {
      return "正在检索知识库并生成建议";
    }

    return "AI 只提供辅助建议，最终处理由人工客服确认";
  }, [recommendationLoading, summaryLoading]);

  async function handleGenerateSummary() {
    setError("");
    setRecommendation(null);
    setSummaryLoading(true);

    try {
      const response = await generateSummary(chatHistory);
      setSummary(response.summary);
      setSummaryRawText(response.raw_text);

      if (!currentIssue.trim()) {
        setCurrentIssue(response.summary.user_issue);
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : "生成总结失败");
    } finally {
      setSummaryLoading(false);
    }
  }

  async function handleGetRecommendation() {
    if (!summary) {
      return;
    }

    setError("");
    setRecommendationLoading(true);

    try {
      const response = await getRecommendation(currentIssue, summary);
      setRecommendation(response);
    } catch (error) {
      setError(error instanceof Error ? error.message : "获取推荐方案失败");
    } finally {
      setRecommendationLoading(false);
    }
  }

  return (
    <main className="workspace">
      <header className="topbar">
        <div>
          <p className="eyebrow">MVP Demo</p>
          <h1>AI 客诉辅助 Copilot</h1>
        </div>
        <div className="status-pill">{statusText}</div>
      </header>

      {error ? <div className="error-banner">{error}</div> : null}

      <div className="three-column-layout">
        <ChatInputPanel
          value={chatHistory}
          isLoading={summaryLoading}
          onChange={setChatHistory}
          onGenerate={handleGenerateSummary}
        />

        <SummaryPanel summary={summary} rawText={summaryRawText} />

        <RecommendationPanel
          currentIssue={currentIssue}
          summary={summary}
          result={recommendation}
          isLoading={recommendationLoading}
          onIssueChange={setCurrentIssue}
          onRecommend={handleGetRecommendation}
        />
      </div>
    </main>
  );
}
