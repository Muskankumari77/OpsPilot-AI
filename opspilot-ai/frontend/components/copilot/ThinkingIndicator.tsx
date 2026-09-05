import { Sparkles } from "lucide-react";

export function ThinkingIndicator() {
  return (
    <div className="chat-message flex justify-start">
      <div className="flex items-end gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-xl border border-border bg-white text-accent-primary shadow-sm dark:bg-[#181629]">
          <Sparkles size={16} />
        </div>

        <div className="flex items-center gap-1.5 rounded-2xl rounded-bl-md border border-border bg-white px-5 py-4 shadow-soft dark:bg-[#181629]">
          <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-accent-primary [animation-delay:-0.3s]" />

          <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-accent-secondary [animation-delay:-0.15s]" />

          <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-accent-pink" />
        </div>
      </div>
    </div>
  );
}