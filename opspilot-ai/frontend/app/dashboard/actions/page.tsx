"use client";

import { useActions } from "@/hooks/useActions";
import type { Action } from "@/types/operations";

const STATUS_OPTIONS: Action["status"][] = ["pending", "in_progress", "completed", "cancelled"];

const PRIORITY_STYLES: Record<Action["priority"], string> = {
  high: "bg-status-danger/15 text-status-danger",
  medium: "bg-status-warning/15 text-status-warning",
  low: "bg-accent-cyan/10 text-accent-cyan",
};

export default function ActionsPage() {
  const { actions, isLoading, updateStatus } = useActions();

  return (
    <main className="px-6 py-8">
      <h1 className="font-display text-2xl font-semibold">Action Center</h1>
      <p className="mt-1 text-sm text-text-muted">
        Tasks created from AI recommendations and manual decisions.
      </p>

      {isLoading && <p className="mt-8 text-sm text-text-muted">Loading actions...</p>}

      {!isLoading && actions.length === 0 && (
        <p className="mt-8 text-sm text-text-muted">
          No actions yet. Recommendations shown around the dashboard can be converted
          into actions (via the API — a one-click &quot;Create action&quot; button here
          is a natural next addition).
        </p>
      )}

      {!isLoading && actions.length > 0 && (
        <div className="mt-6 space-y-3">
          {actions.map((action) => (
            <div key={action.id} className="rounded-card border border-border bg-background-card p-4">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium">{action.title}</p>
                <span className={`rounded-full px-2.5 py-0.5 text-xs uppercase ${PRIORITY_STYLES[action.priority]}`}>
                  {action.priority}
                </span>
              </div>
              {action.description && <p className="mt-1 text-sm text-text-muted">{action.description}</p>}
              <div className="mt-3 flex items-center gap-3">
                <select
                  value={action.status}
                  onChange={(e) => updateStatus(action.id, e.target.value as Action["status"])}
                  className="rounded-lg border border-border bg-background-surface px-2.5 py-1.5 text-xs outline-none focus:border-accent-indigo"
                >
                  {STATUS_OPTIONS.map((s) => (
                    <option key={s} value={s}>
                      {s.replace("_", " ")}
                    </option>
                  ))}
                </select>
                {action.owner && <span className="text-xs text-text-muted">Owner: {action.owner}</span>}
                {action.due_date && <span className="text-xs text-text-muted">Due: {action.due_date}</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}
