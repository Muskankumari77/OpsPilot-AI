"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  ArrowRight,
  BarChart3,
  BrainCircuit,
  CheckCircle2,
  Database,
  LineChart,
  Sparkles,
  TrendingUp,
  ShieldCheck,
  Zap,
} from "lucide-react";

type HealthResponse = {
  status: string;
  app: string;
  environment: string;
  database: string;
};

export default function Home() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const apiUrl =
      process.env.NEXT_PUBLIC_API_URL ??
      "http://localhost:8000/api/v1";

    fetch(`${apiUrl}/health`)
      .then((res) => res.json())
      .then(setHealth)
      .catch(() =>
        setError("Backend is currently offline.")
      );
  }, []);

  return (
    <main className="min-h-screen overflow-hidden bg-background">
      {/* NAVBAR */}

      <header className="relative z-20 border-b border-white/60 bg-white/70 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5 lg:px-8">
          <Link
            href="/"
            className="flex items-center gap-3"
          >
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-accent-primary to-accent-pink shadow-glow">
              <Sparkles
                size={21}
                className="text-white"
              />
            </div>

            <div>
              <p className="font-display text-lg font-bold tracking-tight">
                OpsPilot AI
              </p>
              <p className="text-[10px] font-medium uppercase tracking-[0.18em] text-text-muted">
                Business Intelligence
              </p>
            </div>
          </Link>

          <nav className="hidden items-center gap-8 text-sm text-text-muted md:flex">
            <a href="#features" className="hover:text-text-primary">
              Features
            </a>
            <a href="#how-it-works" className="hover:text-text-primary">
              How it works
            </a>
            <a href="#intelligence" className="hover:text-text-primary">
              Intelligence
            </a>
          </nav>

          <div className="flex items-center gap-3">
            <Link
              href="/login"
              className="rounded-xl border border-border bg-white px-4 py-2.5 text-sm font-medium transition hover:border-accent-primary/40 hover:bg-accent-primary/5"
            >
              Log in
            </Link>

            <Link
              href="/signup"
              className="gradient-button rounded-xl px-5 py-2.5 text-sm font-semibold text-white transition"
            >
              Get Started
              <ArrowRight
                size={15}
                className="ml-1 inline"
              />
            </Link>
          </div>
        </div>
      </header>

      {/* HERO */}

      <section className="relative">
        <div className="hero-glow left-[-100px] top-20" />
        <div className="hero-glow right-[-180px] top-32" />

        <div className="mx-auto grid max-w-7xl items-center gap-16 px-6 pb-20 pt-20 lg:grid-cols-2 lg:px-8 lg:pb-28 lg:pt-28">
          <div className="relative z-10">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-accent-primary/15 bg-white/80 px-4 py-2 text-xs font-semibold text-accent-primary shadow-sm">
              <span className="h-2 w-2 animate-pulse-soft rounded-full bg-accent-cyan" />
              AI-powered business intelligence
            </div>

            <h1 className="max-w-3xl font-display text-5xl font-bold leading-[1.05] tracking-[-0.04em] text-text-primary sm:text-6xl lg:text-7xl">
              Your data.
              <br />
              Your decisions.
              <br />
              <span className="gradient-text">
                Smarter with AI.
              </span>
            </h1>

            <p className="mt-7 max-w-xl text-lg leading-8 text-text-muted">
              OpsPilot AI turns your sales, inventory, customers and
              expenses into clear insights, predictions and decisions —
              all from one intelligent workspace.
            </p>

            <div className="mt-9 flex flex-wrap gap-4">
              <Link
                href="/signup"
                className="gradient-button inline-flex items-center gap-2 rounded-2xl px-7 py-4 font-semibold text-white transition"
              >
                Start for free
                <ArrowRight size={18} />
              </Link>

              <Link
                href="/login"
                className="inline-flex items-center gap-2 rounded-2xl border border-border bg-white px-7 py-4 font-semibold text-text-primary shadow-sm transition hover:-translate-y-0.5 hover:shadow-soft"
              >
                Explore dashboard
              </Link>
            </div>

            <div className="mt-8 flex flex-wrap gap-5 text-sm text-text-muted">
              <div className="flex items-center gap-2">
                <CheckCircle2
                  size={16}
                  className="text-status-success"
                />
                No credit card
              </div>

              <div className="flex items-center gap-2">
                <CheckCircle2
                  size={16}
                  className="text-status-success"
                />
                AI insights
              </div>

              <div className="flex items-center gap-2">
                <CheckCircle2
                  size={16}
                  className="text-status-success"
                />
                Forecasting
              </div>
            </div>
          </div>

          {/* HERO VISUAL */}

          <div className="relative min-h-[500px]">
            <div className="absolute inset-0 rounded-[3rem] bg-gradient-to-br from-accent-primary/10 via-accent-pink/10 to-accent-blue/10 blur-3xl" />

            <div className="glass absolute left-4 top-10 w-[85%] rounded-[2rem] p-5 shadow-glow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-text-muted">
                    Revenue overview
                  </p>
                  <p className="mt-1 text-3xl font-bold">
                    $125,430
                  </p>
                </div>

                <div className="rounded-xl bg-status-success/10 px-3 py-2 text-xs font-bold text-status-success">
                  ↑ 12.4%
                </div>
              </div>

              <div className="mt-7 flex h-40 items-end gap-2">
                {[32, 45, 38, 58, 52, 75, 68, 88, 80, 98].map(
                  (height, index) => (
                    <div
                      key={index}
                      className="flex-1 rounded-t-lg bg-gradient-to-t from-accent-primary to-accent-pink opacity-80"
                      style={{ height: `${height}%` }}
                    />
                  )
                )}
              </div>
            </div>

            <div className="float-card glass absolute right-0 top-52 w-56 rounded-2xl p-5 shadow-soft">
              <div className="flex items-center gap-3">
                <div className="rounded-xl bg-accent-primary/10 p-3">
                  <TrendingUp
                    size={20}
                    className="text-accent-primary"
                  />
                </div>

                <div>
                  <p className="text-xs text-text-muted">
                    Growth
                  </p>
                  <p className="font-bold text-status-success">
                    +18.6%
                  </p>
                </div>
              </div>

              <p className="mt-4 text-sm text-text-muted">
                Business performance is trending upward.
              </p>
            </div>

            <div className="float-card-delay glass absolute bottom-3 left-16 w-64 rounded-2xl p-5 shadow-soft">
              <div className="flex items-center gap-3">
                <div className="rounded-xl bg-accent-pink/10 p-3">
                  <BrainCircuit
                    size={21}
                    className="text-accent-pink"
                  />
                </div>

                <div>
                  <p className="text-xs text-text-muted">
                    AI Copilot
                  </p>
                  <p className="text-sm font-semibold">
                    24 insights found
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FEATURES */}

      <section
        id="features"
        className="border-y border-border bg-white/60 py-24"
      >
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <p className="text-sm font-bold uppercase tracking-widest text-accent-primary">
              Everything in one place
            </p>

            <h2 className="mt-3 font-display text-4xl font-bold tracking-tight">
              From raw data to
              <span className="gradient-text"> real decisions.</span>
            </h2>

            <p className="mt-4 text-text-muted">
              Stop jumping between spreadsheets and dashboards.
              OpsPilot brings your business intelligence together.
            </p>
          </div>

          <div className="mt-14 grid gap-5 md:grid-cols-2 lg:grid-cols-4">
            {[
              {
                icon: BarChart3,
                title: "Understand",
                text: "See your sales, customers and business performance clearly.",
                color: "text-accent-primary",
                bg: "bg-accent-primary/10",
              },
              {
                icon: LineChart,
                title: "Predict",
                text: "Forecast future revenue and demand using machine learning.",
                color: "text-accent-blue",
                bg: "bg-accent-blue/10",
              },
              {
                icon: Zap,
                title: "Detect",
                text: "Find unusual sales, inventory and operational patterns.",
                color: "text-accent-pink",
                bg: "bg-accent-pink/10",
              },
              {
                icon: BrainCircuit,
                title: "Ask AI",
                text: "Ask business questions in plain English and get grounded answers.",
                color: "text-accent-secondary",
                bg: "bg-accent-secondary/10",
              },
            ].map((feature) => {
              const Icon = feature.icon;

              return (
                <div
                  key={feature.title}
                  className="group rounded-3xl border border-border bg-white p-7 shadow-sm transition duration-300 hover:-translate-y-2 hover:shadow-glow"
                >
                  <div
                    className={`mb-6 flex h-12 w-12 items-center justify-center rounded-2xl ${feature.bg}`}
                  >
                    <Icon
                      size={23}
                      className={feature.color}
                    />
                  </div>

                  <h3 className="text-lg font-bold">
                    {feature.title}
                  </h3>

                  <p className="mt-3 text-sm leading-6 text-text-muted">
                    {feature.text}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* INTELLIGENCE */}

      <section
        id="intelligence"
        className="relative overflow-hidden py-24"
      >
        <div className="mx-auto grid max-w-7xl items-center gap-14 px-6 lg:grid-cols-2 lg:px-8">
          <div>
            <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-accent-primary to-accent-pink shadow-glow">
              <Sparkles
                size={23}
                className="text-white"
              />
            </div>

            <h2 className="font-display text-4xl font-bold tracking-tight sm:text-5xl">
              Meet your AI
              <br />
              <span className="gradient-text">
                business analyst.
              </span>
            </h2>

            <p className="mt-5 max-w-xl text-lg leading-8 text-text-muted">
              Ask questions like:
            </p>

            <div className="mt-5 space-y-3">
              {[
                "Which customers are likely to churn?",
                "What are my top products this month?",
                "Why did revenue change?",
                "Which inventory needs attention?",
              ].map((question) => (
                <div
                  key={question}
                  className="flex items-center gap-3 rounded-2xl border border-border bg-white p-4 shadow-sm"
                >
                  <Sparkles
                    size={17}
                    className="text-accent-primary"
                  />
                  <span className="text-sm font-medium">
                    {question}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="relative">
            <div className="absolute inset-0 rounded-[3rem] bg-gradient-to-br from-accent-primary/20 to-accent-pink/20 blur-3xl" />

            <div className="relative rounded-[2rem] border border-white bg-gradient-to-br from-[#6655ff] to-[#a14bdf] p-6 shadow-glow">
              <div className="rounded-[1.5rem] bg-white/95 p-6">
                <div className="flex items-center gap-3">
                  <div className="rounded-xl bg-accent-primary/10 p-3">
                    <BrainCircuit
                      size={22}
                      className="text-accent-primary"
                    />
                  </div>

                  <div>
                    <p className="font-bold">
                      Ask OpsPilot
                    </p>
                    <p className="text-xs text-text-muted">
                      Your AI business analyst
                    </p>
                  </div>
                </div>

                <div className="mt-8 rounded-2xl border border-border bg-background-soft p-4 text-sm text-text-muted">
                  Show me customers likely to churn...
                </div>

                <div className="mt-4 rounded-2xl bg-gradient-to-r from-accent-primary/10 to-accent-pink/10 p-5">
                  <p className="text-sm font-semibold">
                    AI analysis
                  </p>

                  <p className="mt-2 text-sm leading-6 text-text-muted">
                    37 customers show elevated churn risk based
                    on recent purchase frequency and recency.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* TRUST / DATA */}

      <section
        id="how-it-works"
        className="bg-[#11142D] py-20 text-white"
      >
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="grid gap-10 md:grid-cols-3">
            <div>
              <Database className="text-accent-cyan" />
              <h3 className="mt-5 text-xl font-bold">
                Connect your data
              </h3>
              <p className="mt-3 text-sm leading-6 text-white/60">
                Upload sales, customers, products, inventory and
                expenses.
              </p>
            </div>

            <div>
              <BarChart3 className="text-accent-primary" />
              <h3 className="mt-5 text-xl font-bold">
                Understand your business
              </h3>
              <p className="mt-3 text-sm leading-6 text-white/60">
                Explore dashboards, KPIs, trends and operational
                insights.
              </p>
            </div>

            <div>
              <ShieldCheck className="text-accent-pink" />
              <h3 className="mt-5 text-xl font-bold">
                Make better decisions
              </h3>
              <p className="mt-3 text-sm leading-6 text-white/60">
                Use AI, forecasting and anomaly detection to act
                earlier.
              </p>
            </div>
          </div>

          <div className="mt-16 border-t border-white/10 pt-8 text-center text-sm text-white/50">
            OpsPilot AI — From data to decisions.
          </div>
        </div>
      </section>

      {/* BACKEND STATUS */}

      <div className="fixed bottom-5 right-5 z-50 hidden sm:block">
        <div className="rounded-2xl border border-white/70 bg-white/85 px-4 py-3 shadow-soft backdrop-blur-xl">
          <div className="flex items-center gap-3">
            <div
              className={`h-2.5 w-2.5 rounded-full ${
                health
                  ? "bg-status-success"
                  : error
                  ? "bg-status-danger"
                  : "animate-pulse bg-accent-primary"
              }`}
            />

            <div>
              <p className="text-xs font-semibold">
                OpsPilot backend
              </p>

              <p className="text-[11px] text-text-muted">
                {health
                  ? "Connected"
                  : error
                  ? "Offline"
                  : "Checking..."}
              </p>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}