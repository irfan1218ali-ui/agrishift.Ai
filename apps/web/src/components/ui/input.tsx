import * as React from "react";
import { cn } from "@/lib/utils";

export const Input = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(function Input(
  { className, type = "text", ...props }, ref,
) {
  return <input ref={ref} type={type} className={cn("flex h-11 w-full rounded-xl border border-slate-300 bg-white px-3.5 text-sm text-slate-950 outline-none placeholder:text-slate-500 focus-visible:ring-2 focus-visible:ring-green-700 focus-visible:ring-offset-1 disabled:cursor-not-allowed disabled:opacity-50", className)} {...props} />;
});
