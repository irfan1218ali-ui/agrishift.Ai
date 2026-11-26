"use client";

import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";
import { t } from "@/lib/i18n";

export function LandingDataModeBadge() {
  const [mode, setMode] = useState<"REAL" | "DEMO" | "unavailable" | null>(null);

  useEffect(() => {
    let active = true;
    api.health().then((health) => {
      if (!active) return;
      setMode(health.data_mode === "REAL" || health.data_mode === "DEMO" ? health.data_mode : "unavailable");
    }).catch(() => { if (active) setMode("unavailable"); });
    return () => { active = false; };
  }, []);

  const label = mode === "REAL" ? t("en", "real") : mode === "DEMO" ? t("en", "demo") : mode === "unavailable" ? t("en", "dataModeUnavailable") : "CHECKING DATA MODE";
  const tone = mode === "REAL" ? "green" : mode === "DEMO" ? "amber" : "neutral";
  return <Badge tone={tone} aria-live="polite" aria-label={`Application data mode: ${label}`}>{label}</Badge>;
}
