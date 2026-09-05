import type { DisplayMessage } from "@/hooks/useCopilot";
import { Bot, User } from "lucide-react";

export function MessageBubble({
  message,
}: {
  message: DisplayMessage;
}) {
  const isUser = message.role === "user";

  return (
    <div
      className={`chat-message flex w-full ${
        isUser
          ? "justify-end"
          : "justify-start"
      }`}
    >
      <div
        className={`flex max-w-[88%] items-end gap-3 sm:max-w-[78%] ${
          isUser
            ? "flex-row-reverse"
            : "flex-row"
        }`}
      >
        {/* AVATAR */}

        <div
          className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-xl ${
            isUser
              ? "bg-gradient-to-br from-accent-primary to-accent-pink text-white shadow-glow"
              : "border border-border bg-white text-accent-primary shadow-sm dark:bg-[#181629]"
          }`}
        >
          {isUser ? (
            <User size={16} />
          ) : (
            <Bot size={17} />
          )}
        </div>

        {/* MESSAGE */}

        <div className="min-w-0">
          <div
            className={`whitespace-pre-wrap break-words rounded-2xl px-4 py-3 text-sm leading-6 ${
              isUser
                ? "rounded-br-md bg-gradient-to-r from-accent-primary to-accent-pink text-white shadow-glow"
                : "rounded-bl-md border border-border bg-white text-text-primary shadow-soft dark:bg-[#181629] dark:text-[#f8f7ff]"
            }`}
          >
            {message.content}
          </div>

          {/* DOMAINS */}

          {!isUser &&
            message.domains &&
            message.domains.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1.5">
                {message.domains.map(
                  (domain) => (
                    <span
                      key={domain}
                      className="rounded-full border border-accent-primary/15 bg-accent-primary/5 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wide text-accent-primary dark:bg-accent-primary/10"
                    >
                      {domain}
                    </span>
                  )
                )}
              </div>
            )}
        </div>
      </div>
    </div>
  );
}