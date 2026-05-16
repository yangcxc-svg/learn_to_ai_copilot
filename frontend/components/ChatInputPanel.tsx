"use client";

import { WandSparkles } from "lucide-react";

type ChatInputPanelProps = {
  value: string;
  isLoading: boolean;
  onChange: (value: string) => void;
  onGenerate: () => void;
};

export function ChatInputPanel({
  value,
  isLoading,
  onChange,
  onGenerate
}: ChatInputPanelProps) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">历史沟通</p>
          <h2>聊天记录输入</h2>
        </div>
      </div>

      <textarea
        className="textarea large"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="粘贴用户与客服的历史聊天记录..."
      />

      <button
        className="primary-button"
        type="button"
        onClick={onGenerate}
        disabled={isLoading || value.trim().length === 0}
      >
        <WandSparkles size={18} />
        <span>{isLoading ? "生成中" : "生成总结"}</span>
      </button>
    </section>
  );
}

