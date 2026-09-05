"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  ShoppingCart,
  Package,
  Users,
  Receipt,
  UploadCloud,
  TrendingUp,
  AlertTriangle,
  Sparkles,
  BookOpen,
  ListChecks,
  Bell,
  FileText,
  Settings,
  ChevronRight,
} from "lucide-react";

const NAV_ITEMS = [
  {
    href: "/dashboard",
    label: "Overview",
    icon: LayoutDashboard,
  },
  {
    href: "/dashboard/sales",
    label: "Sales",
    icon: ShoppingCart,
  },
  {
    href: "/dashboard/inventory",
    label: "Inventory",
    icon: Package,
  },
  {
    href: "/dashboard/customers",
    label: "Customers",
    icon: Users,
  },
  {
    href: "/dashboard/expenses",
    label: "Expenses",
    icon: Receipt,
  },
  {
    href: "/dashboard/forecasts",
    label: "Forecasts",
    icon: TrendingUp,
  },
  {
    href: "/dashboard/anomalies",
    label: "Anomalies",
    icon: AlertTriangle,
  },
  {
    href: "/dashboard/copilot",
    label: "Ask OpsPilot",
    icon: Sparkles,
  },
  {
    href: "/dashboard/knowledge-base",
    label: "Knowledge Base",
    icon: BookOpen,
  },
  {
    href: "/dashboard/actions",
    label: "Actions",
    icon: ListChecks,
  },
  {
    href: "/dashboard/alerts",
    label: "Alerts",
    icon: Bell,
  },
  {
    href: "/dashboard/reports",
    label: "Reports",
    icon: FileText,
  },
  {
    href: "/dashboard/data",
    label: "Data",
    icon: UploadCloud,
  },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden w-[245px] shrink-0 border-r border-border bg-white md:flex md:flex-col">
      {/* BRAND */}

      <div className="px-6 py-6">
        <Link
          href="/dashboard"
          className="flex items-center gap-3"
        >
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-accent-primary to-accent-pink shadow-glow">
            <Sparkles
              size={20}
              className="text-white"
            />
          </div>

          <div>
            <p className="font-display text-lg font-bold tracking-tight">
              OpsPilot AI
            </p>

            <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-text-muted">
              Intelligence
            </p>
          </div>
        </Link>
      </div>

      {/* NAVIGATION */}

      <nav className="flex-1 space-y-1 overflow-y-auto px-3 pb-5">
        <p className="mb-3 px-3 text-[10px] font-bold uppercase tracking-[0.18em] text-text-soft">
          Workspace
        </p>

        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;

          const isActive =
            pathname === item.href ||
            (item.href !== "/dashboard" &&
              pathname.startsWith(item.href));

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all ${
                isActive
                  ? "bg-gradient-to-r from-accent-primary to-accent-secondary text-white shadow-glow"
                  : "text-text-muted hover:bg-background-soft hover:text-text-primary"
              }`}
            >
              <Icon size={17} />

              <span className="flex-1">
                {item.label}
              </span>

              {isActive && (
                <ChevronRight size={15} />
              )}
            </Link>
          );
        })}
      </nav>

      {/* BOTTOM AI CARD */}

      <div className="border-t border-border p-4">
        <div className="rounded-2xl bg-gradient-to-br from-accent-primary/10 via-accent-secondary/10 to-accent-pink/10 p-4">
          <div className="flex items-center gap-2">
            <div className="rounded-lg bg-white p-2 shadow-sm">
              <Sparkles
                size={14}
                className="text-accent-primary"
              />
            </div>

            <span className="text-xs font-bold">
              AI Copilot
            </span>
          </div>

          <p className="mt-3 text-[11px] leading-5 text-text-muted">
            Ask questions about your sales, customers,
            inventory and expenses.
          </p>

          <Link
            href="/dashboard/copilot"
            className="mt-3 inline-flex items-center text-xs font-bold text-accent-primary"
          >
            Ask something
            <ChevronRight size={13} />
          </Link>
        </div>

        <button className="mt-3 flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-text-muted transition hover:bg-background-soft hover:text-text-primary">
          <Settings size={17} />
          Settings
        </button>
      </div>
    </aside>
  );
}