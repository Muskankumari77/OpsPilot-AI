import { ButtonHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  loading?: boolean;
}

export function Button({ loading, children, disabled, className, ...rest }: ButtonProps) {
  return (
    <button
      className={cn(
        "w-full rounded-lg bg-gradient-to-r from-accent-indigo to-accent-violet px-4 py-2.5 text-sm font-medium text-white transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50",
        className
      )}
      disabled={disabled || loading}
      {...rest}
    >
      {loading ? "Please wait..." : children}
    </button>
  );
}
