"use client";

import { useState } from "react";
import type { Story } from "@/lib/parser";

const SOURCE_LABELS: Record<Story["source"], string> = {
  register: "The Register",
  sans: "SANS ISC",
  unknown: "Unknown",
};

interface EscalationState {
  status: "idle" | "loading" | "done" | "error";
  report?: string;
  error?: string;
}

export default function StoryCard({ story }: { story: Story }) {
  const [escalation, setEscalation] = useState<EscalationState>({ status: "idle" });
  const [showReport, setShowReport] = useState(false);

  async function handleEscalate() {
    setEscalation({ status: "loading" });
    try {
      const res = await fetch("/api/escalate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: story.title,
          url: story.url,
          published: story.published,
          summary: story.summary,
        }),
      });
      const text = await res.text();
      if (!res.ok) {
        let message = `HTTP ${res.status}`;
        try { message = JSON.parse(text).error ?? message; } catch { /* HTML error page */ }
        throw new Error(message);
      }
      const data = JSON.parse(text);
      setEscalation({ status: "done", report: data.report });
      setShowReport(true);
    } catch (e) {
      setEscalation({ status: "error", error: e instanceof Error ? e.message : "Unknown error" });
    }
  }

  function handleDownload() {
    if (!escalation.report) return;
    const blob = new Blob([escalation.report], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `escalation_${story.title.toLowerCase().replace(/[^a-z0-9]+/g, "_").slice(0, 50)}.md`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden">
      <div className="px-5 py-4">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                {SOURCE_LABELS[story.source]}
              </span>
              {story.published && (
                <>
                  <span className="text-gray-700">·</span>
                  <span className="text-xs text-gray-500">{story.published}</span>
                </>
              )}
            </div>
            <a
              href={story.url}
              target="_blank"
              rel="noopener noreferrer"
              className="font-semibold text-white hover:text-red-400 transition-colors leading-snug block"
            >
              {story.title}
            </a>
            {story.summary && (
              <p className="text-sm text-gray-400 mt-1 leading-relaxed">{story.summary}</p>
            )}
          </div>

          <div className="flex-shrink-0 flex flex-col items-end gap-2">
            {escalation.status === "idle" && (
              <button
                onClick={handleEscalate}
                title="Escalate"
                className="flex flex-col items-center gap-1 hover:scale-110 active:scale-95 transition-transform"
              >
                <img src="/escalate.png" alt="Escalate" className="h-12 w-auto" />
                <span className="text-xs font-bold text-red-500 uppercase tracking-widest">Escalate</span>
              </button>
            )}
            {escalation.status === "loading" && (
              <span className="text-xs text-gray-500 px-3 py-1.5 flex items-center gap-1.5">
                <svg className="animate-spin h-3 w-3 text-gray-400" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                </svg>
                Generating…
              </span>
            )}
            {escalation.status === "done" && (
              <div className="flex gap-2">
                <button
                  onClick={() => setShowReport((v) => !v)}
                  className="text-xs font-medium px-3 py-1.5 bg-gray-800 hover:bg-gray-700 border border-gray-700 text-gray-300 rounded transition-colors"
                >
                  {showReport ? "Hide" : "View"} report
                </button>
                <button
                  onClick={handleDownload}
                  className="text-xs font-medium px-3 py-1.5 bg-green-900 hover:bg-green-800 border border-green-700 text-green-200 rounded transition-colors"
                >
                  Download .md
                </button>
              </div>
            )}
            {escalation.status === "error" && (
              <div className="text-right">
                <p className="text-xs text-red-400 mb-1">{escalation.error}</p>
                <button
                  onClick={handleEscalate}
                  className="text-xs font-medium px-3 py-1.5 bg-red-900 hover:bg-red-800 border border-red-700 text-red-200 rounded transition-colors"
                >
                  Retry
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {showReport && escalation.report && (
        <div className="border-t border-gray-800 px-5 py-4">
          <div className="prose prose-sm prose-invert max-w-none">
            <pre className="whitespace-pre-wrap text-sm text-gray-300 font-mono leading-relaxed bg-gray-950 rounded p-4 overflow-auto">
              {escalation.report}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
