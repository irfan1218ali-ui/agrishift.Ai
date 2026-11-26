import type { AnalyzePayload, AnalysisResult, Crop, ExpertAnalysisDetail, ExpertAnalysisList, ExpertReview, ExpertSummary, Health, LayerCatalog, StoredAnalysis } from "@/lib/types";

export const API_BASE = (process.env.NEXT_PUBLIC_AGRISHIFT_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, { ...init, cache: "no-store" });
  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    const message = payload?.error?.message || payload?.detail || `Request failed (${response.status})`;
    throw new Error(String(message));
  }
  return payload as T;
}

async function expertRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api/expert/${path}`, { ...init, credentials: "same-origin", cache: "no-store" });
  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    const message = payload?.error?.message || payload?.detail || `Request failed (${response.status})`;
    throw Object.assign(new Error(String(message)), { status: response.status, code: payload?.error?.code });
  }
  return payload as T;
}

export const api = {
  health: () => request<Health>("/api/v1/health"),
  crops: () => request<Crop[]>("/api/v1/crops"),
  layers: () => request<LayerCatalog>("/api/v1/layers/metadata"),
  analyze: (payload: AnalyzePayload) => request<AnalysisResult>("/api/v1/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  }),
  analysis: (id: string) => request<StoredAnalysis>(`/api/v1/analyses/${encodeURIComponent(id)}`),
  context: () => request<Record<string, unknown>>("/api/v1/context"),
  expertMe: () => expertRequest<{ authenticated: true; id: string; email: string; role: "EXPERT" }>("auth/me"),
  expertLogin: (email: string, password: string) => expertRequest<{ authenticated: true; role: "EXPERT"; email: string }>("auth/login", {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email, password }),
  }),
  expertLogout: () => expertRequest<{ authenticated: false }>("auth/logout", { method: "POST" }),
  expertSummary: () => expertRequest<ExpertSummary>("analyses/summary"),
  expertAnalyses: (query: URLSearchParams) => expertRequest<ExpertAnalysisList>(`analyses?${query.toString()}`),
  expertAnalysis: (id: string) => expertRequest<ExpertAnalysisDetail>(`analyses/${encodeURIComponent(id)}`),
  expertReviews: (id: string) => expertRequest<{ items: ExpertReview[] }>(`analyses/${encodeURIComponent(id)}/reviews`),
  createReview: (id: string, body: Partial<Pick<ExpertReview, "decision" | "comments" | "suggested_rotation" | "soil_test_requested">>) => expertRequest<ExpertReview>(`analyses/${encodeURIComponent(id)}/reviews`, {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
  }),
  updateReview: (reviewId: string, body: Partial<Pick<ExpertReview, "decision" | "comments" | "suggested_rotation" | "soil_test_requested">>) => expertRequest<ExpertReview>(`reviews/${encodeURIComponent(reviewId)}`, {
    method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
  }),
  expertNotes: (id: string) => expertRequest<import("@/lib/types").ExpertNote>(`analyses/${encodeURIComponent(id)}/notes`),
  saveExpertNotes: (id: string, content: string) => expertRequest<import("@/lib/types").ExpertNote>(`analyses/${encodeURIComponent(id)}/notes`, {
    method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ content }),
  }),
};

export function analysisIds(): string[] {
  if (typeof window === "undefined") return [];
  try {
    const value = JSON.parse(window.localStorage.getItem("agrishift:analysis-ids") || "[]");
    return Array.isArray(value) ? value.filter((id): id is string => typeof id === "string") : [];
  } catch {
    return [];
  }
}

export function rememberAnalysis(id: string) {
  if (typeof window === "undefined") return;
  const ids = [id, ...analysisIds().filter((item) => item !== id)].slice(0, 50);
  window.localStorage.setItem("agrishift:analysis-ids", JSON.stringify(ids));
}
