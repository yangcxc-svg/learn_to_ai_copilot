"use client";

import type { SummaryResult } from "@/lib/api";
import { CopyButton } from "./CopyButton";

type SummaryPanelProps = {
  summary: SummaryResult | null;
  rawText: string;
};

const labels: Array<[keyof SummaryResult, string]> = [
  ["user_issue", "用户遇到的问题"],
  ["progress", "当前处理进度"],
  ["emotion", "用户情绪状态"],
  ["compensation", "是否已有补偿"],
  ["pending_items", "当前待解决事项"]
];

export function SummaryPanel({ summary, rawText }: SummaryPanelProps) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">AI Summary</p>
          <h2>结构化总结</h2>
        </div>
        <CopyButton text={rawText} disabled={!summary} />
      </div>

      {summary ? (
        <div className="summary-list">
          {labels.map(([key, label]) => (
            <div className="summary-item" key={key}>
              <span>{label}</span>
              <p>{summary[key]}</p>
            </div>
          ))}
        </div>
      ) : (
        <div className="empty-state">
          生成后将在这里展示问题、进度、情绪、补偿和待处理事项。
        </div>
      )}
    </section>
  );
}

