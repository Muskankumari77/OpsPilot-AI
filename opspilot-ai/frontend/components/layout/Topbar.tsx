"use client";

import { useEffect, useState } from "react";
import {
  Bell,
  ChevronDown,
  Search,
  Sparkles,
  Sun,
  Moon,
} from "lucide-react";
import { useAuth } from "@/hooks/useAuth";

export function Topbar() {
  const {
    user,
    activeOrgId,
    switchOrganization,
    logout,
  } = useAuth();

  const [isOrgMenuOpen, setIsOrgMenuOpen] =
    useState(false);

  const [darkMode, setDarkMode] =
    useState(false);

  const activeMembership =
    user?.memberships.find(
      (m) => m.organization.id === activeOrgId
    );

  useEffect(() => {
    const savedTheme =
      localStorage.getItem("opspilot-theme");

    if (savedTheme === "dark") {
      setDarkMode(true);

      document.documentElement.classList.add(
        "dark"
      );
    }
  }, []);

  function toggleTheme() {
    const next = !darkMode;

    setDarkMode(next);

    if (next) {
      document.documentElement.classList.add(
        "dark"
      );

      localStorage.setItem(
        "opspilot-theme",
        "dark"
      );
    } else {
      document.documentElement.classList.remove(
        "dark"
      );

      localStorage.setItem(
        "opspilot-theme",
        "light"
      );
    }
  }

  const firstName =
    user?.full_name?.split(" ")[0] ?? "User";

  return (
    <header className="sticky top-0 z-40 flex h-[76px] items-center justify-between border-b border-border bg-white/80 px-5 backdrop-blur-xl lg:px-7">
      {/* SEARCH */}

      <div className="hidden max-w-xl flex-1 md:block">
        <div className="flex items-center gap-3 rounded-2xl border border-border bg-background-soft/70 px-4 py-2.5 transition-all focus-within:border-accent-primary/40 focus-within:bg-white">
          <Search
            size={18}
            className="text-text-soft"
          />

          <input
            placeholder="Search anything..."
            className="w-full bg-transparent text-sm text-text-primary placeholder:text-text-soft"
          />

          <kbd className="rounded-lg border border-border bg-white px-2 py-1 text-[10px] font-medium text-text-soft">
            Ctrl K
          </kbd>
        </div>
      </div>

      {/* RIGHT */}

      <div className="ml-auto flex items-center gap-2.5">
        {/* AI READY */}

        <div className="hidden items-center gap-2 rounded-xl bg-gradient-to-r from-accent-primary/10 to-accent-pink/10 px-3.5 py-2 sm:flex">
          <Sparkles
            size={15}
            className="text-accent-primary"
          />

          <span className="text-xs font-semibold text-text-primary">
            AI Ready
          </span>
        </div>

        {/* THEME TOGGLE */}

        <button
          onClick={toggleTheme}
          title={
            darkMode
              ? "Switch to light mode"
              : "Switch to dark mode"
          }
          className="flex h-10 w-10 items-center justify-center rounded-xl border border-border bg-white text-text-muted shadow-sm transition-all hover:-translate-y-0.5 hover:border-accent-primary/30 hover:text-accent-primary dark:bg-[#19172b]"
        >
          {darkMode ? (
            <Sun size={17} />
          ) : (
            <Moon size={17} />
          )}
        </button>

        {/* NOTIFICATIONS */}

        <button className="relative flex h-10 w-10 items-center justify-center rounded-xl border border-border bg-white text-text-muted shadow-sm transition-all hover:-translate-y-0.5 hover:text-text-primary dark:bg-[#19172b]">
          <Bell size={17} />

          <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-accent-pink" />
        </button>

        {/* PROFILE / ORGANIZATION */}

        <div className="relative">
          <button
            onClick={() =>
              setIsOrgMenuOpen(
                (value) => !value
              )
            }
            className="flex items-center gap-3 rounded-xl border border-border bg-white px-2.5 py-1.5 shadow-sm transition hover:bg-background-soft dark:bg-[#19172b]"
          >
            <div className="hidden text-right sm:block">
              <p className="text-xs font-semibold text-text-primary">
                {activeMembership?.organization.name ??
                  "Organization"}
              </p>

              <p className="text-[10px] font-semibold uppercase tracking-wide text-text-soft">
                {activeMembership?.role ?? "Admin"}
              </p>
            </div>

            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-accent-primary to-accent-pink text-sm font-bold text-white shadow-sm">
              {firstName
                .charAt(0)
                .toUpperCase()}
            </div>

            <ChevronDown
              size={15}
              className="text-text-muted"
            />
          </button>

          {/* DROPDOWN */}

          {isOrgMenuOpen && user && (
            <div className="absolute right-0 top-full z-50 mt-2 w-64 rounded-2xl border border-border bg-white p-2 shadow-glow dark:bg-[#151323]">
              <div className="px-3 py-2">
                <p className="text-xs font-semibold text-text-primary">
                  Your organizations
                </p>
              </div>

              {user.memberships.map((membership) => (
                <button
                  key={
                    membership.organization.id
                  }
                  onClick={() => {
                    switchOrganization(
                      membership.organization.id
                    );

                    setIsOrgMenuOpen(false);
                  }}
                  className={`flex w-full items-center justify-between rounded-xl px-3 py-2.5 text-left text-sm transition hover:bg-background-soft ${
                    membership.organization.id ===
                    activeOrgId
                      ? "text-accent-primary"
                      : "text-text-primary"
                  }`}
                >
                  <span>
                    {membership.organization.name}
                  </span>

                  <span className="text-[10px] font-semibold uppercase text-text-soft">
                    {membership.role}
                  </span>
                </button>
              ))}

              <div className="my-2 border-t border-border" />

              <button
                onClick={logout}
                className="w-full rounded-xl px-3 py-2.5 text-left text-sm font-medium text-status-danger transition hover:bg-status-danger/5"
              >
                Log out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}