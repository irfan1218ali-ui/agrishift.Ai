import * as React from "react";
import { cn } from "@/lib/utils";

export function Badge({ className, tone = "neutral", ...props }: React.HTMLAttributes<HTMLSpanElement> & { tone?: "neutral" | "green" | "amber" | "red" | "blue" }) {
  const tones = {
    neutral: "bg-slate-100 text-slate-700",
    green: "bg-green-100 text-green-900",
    amber: "bg-amber-100 text-amber-950",
    red: "bg-red-100 text-red-900",
    blue: "bg-blue-100 text-blue-900",
  };
  return <span className={cn("inline-flex min-h-6 items-center rounded-full px-2.5 text-xs font-semibold", tones[tone], className)} {...props} />;
}
