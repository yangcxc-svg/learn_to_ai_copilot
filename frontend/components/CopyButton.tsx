"use client";

import { Check, Copy } from "lucide-react";
import { useState } from "react";

type CopyButtonProps = {
  text: string;
  disabled?: boolean;
};

export function CopyButton({ text, disabled }: CopyButtonProps) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    if (!text || disabled) {
      return;
    }

    await navigator.clipboard.writeText(text);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1400);
  }

  return (
    <button
      className="icon-button"
      type="button"
      onClick={handleCopy}
      disabled={disabled || !text}
      title={copied ? "已复制" : "一键复制"}
      aria-label={copied ? "已复制" : "一键复制"}
    >
      {copied ? <Check size={18} /> : <Copy size={18} />}
      <span>{copied ? "已复制" : "复制"}</span>
    </button>
  );
}

