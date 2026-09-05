"use client";

import { useState } from "react";
import {
  ArrowUp,
  BrainCircuit,
  Sparkles,
} from "lucide-react";

import { useCopilot } from "@/hooks/useCopilot";
import { MessageBubble } from "@/components/copilot/MessageBubble";
import { ThinkingIndicator } from "@/components/copilot/ThinkingIndicator";

const SUGGESTIONS = [
  {
    label: "Highest expense",
    question: "What is my highest expense?",
  },
  {
    label: "Top products",
    question:
      "Show my top 5 products by revenue.",
  },
  {
    label: "Customers likely to churn",
    question:
      "Show customers likely to churn.",
  },
  {
    label: "Inventory risk",
    question:
      "Which products should I reorder?",
  },
];

export default function CopilotPage() {
  const {
    messages,
    sendMessage,
    isThinking,
    error,
  } = useCopilot();

  const [input, setInput] =
    useState("");

  function handleSend(text: string) {
    const trimmed = text.trim();

    if (!trimmed || isThinking) {
      return;
    }

    sendMessage(trimmed);

    setInput("");
  }

  return (
    <main className="dashboard-grid flex h-[calc(100vh-76px)] min-h-0 flex-col overflow-hidden">

      {/* HEADER */}

      <div className="shrink-0 border-b border-border bg-white/75 px-5 py-5 backdrop-blur-xl dark:bg-[#11101d]/80 lg:px-8">

        <div className="flex items-center gap-4">

          <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-accent-primary to-accent-pink shadow-glow">
            <BrainCircuit
              size={22}
              className="text-white"
            />
          </div>

          <div>
            <div className="flex flex-wrap items-center gap-2">

              <h1 className="font-display text-xl font-bold tracking-tight text-text-primary sm:text-2xl">
                Ask OpsPilot
              </h1>

              <span className="rounded-full bg-status-success/10 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wide text-status-success">
                AI Online
              </span>

            </div>

            <p className="mt-1 text-xs text-text-muted sm:text-sm">
              Your AI business analyst — grounded in your real business data.
            </p>
          </div>

        </div>
      </div>

      {/* CHAT */}

      <div className="min-h-0 flex-1 overflow-y-auto px-4 py-6 sm:px-6 lg:px-10">

        <div className="mx-auto flex max-w-4xl flex-col gap-5">

          {/* EMPTY STATE */}

          {messages.length === 0 && (
            <div className="py-5 sm:py-10">

              <div className="mx-auto max-w-2xl text-center">

                <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-3xl bg-gradient-to-br from-accent-primary/15 to-accent-pink/15">
                  <Sparkles
                    size={29}
                    className="text-accent-primary"
                  />
                </div>

                <h2 className="mt-5 font-display text-2xl font-bold tracking-tight text-text-primary sm:text-3xl">
                  What would you like to know?
                </h2>

                <p className="mx-auto mt-3 max-w-lg text-sm leading-6 text-text-muted">
                  Ask OpsPilot anything about your sales,
                  customers, inventory or expenses.
                </p>

              </div>

              {/* QUESTIONS */}

              <div className="mx-auto mt-8 grid max-w-3xl gap-3 sm:grid-cols-2">

                {SUGGESTIONS.map(
                  (suggestion) => (
                    <button
                      key={suggestion.label}
                      type="button"
                      onClick={() =>
                        handleSend(
                          suggestion.question
                        )
                      }
                      disabled={isThinking}
                      className="group rounded-2xl border border-border bg-white p-4 text-left shadow-sm transition-all hover:-translate-y-1 hover:border-accent-primary/30 hover:shadow-glow disabled:cursor-not-allowed disabled:opacity-50 dark:bg-[#181629]"
                    >

                      <div className="flex items-center justify-between">

                        <span className="text-sm font-semibold text-text-primary">
                          {suggestion.label}
                        </span>

                        <ArrowUp
                          size={15}
                          className="rotate-45 text-text-soft transition group-hover:text-accent-primary"
                        />

                      </div>

                      <p className="mt-2 text-xs leading-5 text-text-muted">
                        {suggestion.question}
                      </p>

                    </button>
                  )
                )}

              </div>

            </div>
          )}

          {/* MESSAGES */}

          {messages.map(
            (message, index) => (
              <MessageBubble
                key={`${message.role}-${index}`}
                message={message}
              />
            )
          )}

          {/* THINKING */}

          {isThinking && (
            <ThinkingIndicator />
          )}

          {/* ERROR */}

          {error && (
            <div className="rounded-2xl border border-status-warning/30 bg-status-warning/10 p-4 text-sm text-status-warning">

              <p className="font-semibold">
                OpsPilot couldn't complete that request.
              </p>

              <p className="mt-1 text-xs leading-5">
                {error}
              </p>

            </div>
          )}

        </div>

      </div>

      {/* INPUT */}

      <div className="shrink-0 border-t border-border bg-white/85 px-4 py-4 backdrop-blur-xl dark:bg-[#11101d]/90 sm:px-6 lg:px-10">

        <div className="mx-auto max-w-4xl">

          {/* QUICK QUESTIONS */}

          {messages.length > 0 && (
            <div className="mb-3 flex gap-2 overflow-x-auto pb-1">

              {SUGGESTIONS.map(
                (suggestion) => (
                  <button
                    key={suggestion.label}
                    type="button"
                    onClick={() =>
                      handleSend(
                        suggestion.question
                      )
                    }
                    disabled={isThinking}
                    className="shrink-0 rounded-full border border-accent-primary/15 bg-accent-primary/5 px-3.5 py-2 text-xs font-medium text-accent-primary transition hover:bg-accent-primary/10 disabled:opacity-50 dark:bg-accent-primary/10"
                  >
                    {suggestion.label}
                  </button>
                )
              )}

            </div>
          )}

          {/* INPUT BOX */}

          <div className="flex items-center gap-2 rounded-2xl border border-border bg-white p-2 shadow-soft transition-all focus-within:border-accent-primary/40 focus-within:shadow-glow dark:bg-[#181629]">

            <input
              value={input}
              onChange={(event) =>
                setInput(event.target.value)
              }
              onKeyDown={(event) => {

                if (
                  event.key === "Enter" &&
                  !event.shiftKey
                ) {
                  event.preventDefault();

                  handleSend(input);
                }

              }}
              placeholder="Ask about sales, inventory, customers, or expenses..."
              disabled={isThinking}
              className="min-w-0 flex-1 bg-transparent px-3 py-3 text-sm text-text-primary placeholder:text-text-soft"
            />

            <button
              type="button"
              onClick={() =>
                handleSend(input)
              }
              disabled={
                isThinking ||
                !input.trim()
              }
              className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-gradient-to-r from-accent-primary to-accent-pink text-white shadow-glow transition-all hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-40"
            >
              <ArrowUp size={19} />
            </button>

          </div>

          <p className="mt-2 text-center text-[10px] text-text-soft">
            OpsPilot answers using your connected business data.
            AI can make mistakes, so verify important decisions.
          </p>

        </div>

      </div>

    </main>
  );
}