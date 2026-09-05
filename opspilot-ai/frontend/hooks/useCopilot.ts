"use client";

import { useState } from "react";
import { apiFetch, ApiError } from "@/lib/api";
import type { ChatMessage, ChatResponse } from "@/types/copilot";

export interface DisplayMessage extends ChatMessage {
  domains?: string[];
}

export function useCopilot() {
  const [messages, setMessages] = useState<DisplayMessage[]>([]);
  const [isThinking, setIsThinking] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function sendMessage(text: string) {
    const userMessage: DisplayMessage = { role: "user", content: text };
    // Backend only expects {role, content} — strip the UI-only `domains` field.
    const history: ChatMessage[] = messages.map(({ role, content }) => ({ role, content }));

    setMessages((prev) => [...prev, userMessage]);
    setIsThinking(true);
    setError(null);

    try {
      const result = await apiFetch<ChatResponse>("/copilot/chat", {
        method: "POST",
        body: JSON.stringify({ message: text, history }),
      });
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: result.response, domains: result.domains_involved },
      ]);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong. Try again.");
    } finally {
      setIsThinking(false);
    }
  }

  return { messages, sendMessage, isThinking, error };
}
