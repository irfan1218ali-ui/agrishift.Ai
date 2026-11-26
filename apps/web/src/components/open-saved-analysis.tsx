"use client";

import { useState } from "react";
import type { FormEvent } from "react";
import { ArrowRight, Search } from "lucide-react";
import { useRouter } from "next/navigation";
import { t } from "@/lib/i18n";

export function OpenSavedAnalysis() {
  const router = useRouter();
  const [analysisId, setAnalysisId] = useState("");
  const [error, setError] = useState("");

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const id = analysisId.trim();
    if (!id) {
      setError(t("en", "analysisIdRequired"));
      return;
    }
    setError("");
    router.push(`/results/${encodeURIComponent(id)}`);
  }

  return (
    <section className="saved-analysis-lookup" aria-labelledby="saved-analysis-title">
      <h2 id="saved-analysis-title">{t("en", "openSavedAnalysis")}</h2>
      <form onSubmit={submit} noValidate>
        <label htmlFor="saved-analysis-id">{t("en", "analysisIdLabel")}</label>
        <div className="saved-analysis-row">
          <input
            id="saved-analysis-id"
            name="analysisId"
            type="text"
            autoComplete="off"
            spellCheck={false}
            value={analysisId}
            placeholder={t("en", "analysisIdPlaceholder")}
            aria-invalid={Boolean(error)}
            aria-describedby={error ? "saved-analysis-error" : undefined}
            onChange={(event) => { setAnalysisId(event.target.value); if (error) setError(""); }}
          />
          <button className="saved-analysis-button" type="submit"><Search size={16} />{t("en", "openAnalysis")}<ArrowRight size={15} /></button>
        </div>
        {error && <p className="saved-analysis-error" id="saved-analysis-error" role="alert">{error}</p>}
      </form>
    </section>
  );
}
