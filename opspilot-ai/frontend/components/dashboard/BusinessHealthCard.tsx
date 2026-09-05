function scoreColor(score: number) {
  if (score >= 75) return "#10B981"; // status-success
  if (score >= 50) return "#F59E0B"; // status-warning
  return "#EF4444"; // status-danger
}

export function BusinessHealthCard({ score }: { score: number }) {
  const radius = 42;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  const color = scoreColor(score);

  return (
    <div className="flex items-center gap-5 rounded-card border border-border bg-gradient-to-br from-accent-indigo/15 to-accent-violet/10 p-5">
      <svg width="100" height="100" viewBox="0 0 100 100" className="shrink-0 -rotate-90">
        <circle cx="50" cy="50" r={radius} fill="none" stroke="#1E2A3E" strokeWidth="8" />
        <circle
          cx="50"
          cy="50"
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
        />
        <text
          x="50"
          y="50"
          textAnchor="middle"
          dominantBaseline="central"
          transform="rotate(90 50 50)"
          className="font-display"
          fontSize="22"
          fontWeight="600"
          fill="#F5F7FA"
        >
          {score}
        </text>
      </svg>
      <div>
        <p className="text-sm text-text-muted">Business Health Score</p>
        <p className="mt-1 text-xs text-text-muted">
          A composite of revenue growth, inventory health, expense control, and
          customer growth — out of 100.
        </p>
      </div>
    </div>
  );
}
