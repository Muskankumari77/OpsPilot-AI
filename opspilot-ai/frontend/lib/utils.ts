import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Merges class names and resolves conflicting Tailwind utilities correctly
 * (e.g. cn("w-full", "w-auto") -> "w-auto"), unlike plain string
 * concatenation where the winning class depends on Tailwind's internal
 * stylesheet order rather than the order passed here.
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
