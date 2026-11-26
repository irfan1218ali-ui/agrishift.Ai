"use client";

import Link from "next/link";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";
import { AlertTriangle, ArrowLeft, CheckCircle2, CircleHelp, ClipboardCheck, MapPin, Satellite, Save } from "lucide-react";
import { AppMap } from "@/components/app-map";
import { ExpertShell } from "@/components/expert-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { api } from "@/lib/api";
import { localizedClusterLabel, t } from "@/lib/i18n";
import { formatDate, number } from "@/lib/utils";
import type { Crop, ExpertAnalysisDetail, ExpertReview, ScoreComponent, StoredAnalysis } from "@/lib/types";

const asNum = (value: unknown): number | undefined => typeof value === "number" && Number.isFinite(value) ? value : undefined;
const componentLabels: Record<string, string> = { base_score: "Base score", seasonal_fit: "Seasonal fit", water_compatibility: "Water compatibility", rotation_diversity: "Rotation diversity", legume_benefit: "Legume benefit", heat_suitability: "Heat suitability", salinity_adjustment: "Salinity adjustment", waterlogging_adjustment: "Waterlogging adjustment", farmer_priority_adjustment: "Farmer priority adjustment", verification_penalty: "Verification penalty", final_score: "Final score" };
const reviewLabels: Record<string, string> = { not_reviewed: "Not reviewed", under_review: "Under review", approved: "Approved", approved_with_changes: "Approved with changes", needs_more_information: "Needs more information", unsuitable: "Unsuitable" };
const decisionOptions = ["approved", "approved_with_changes", "needs_more_information", "unsuitable"] as const;

export default function ExpertAnalysisPage() {
  const params = useParams<{ id: string }>();
  const id = decodeURIComponent(params.id || "");
  const [detail, setDetail] = useState<ExpertAnalysisDetail | null>(null);
  const [crops, setCrops] = useState<Crop[]>([]);
  const [layerOpacity, setLayerOpacity] = useState(0.78);
  const [notes, setNotes] = useState("");
  const [decision, setDecision] = useState("");
  const [comments, setComments] = useState("");
  const [suggestedRotation, setSuggestedRotation] = useState("");
  const [soilTestRequested, setSoilTestRequested] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState("");

  const reload = async () => {
    const value = await api.expertAnalysis(id);
    setDetail(value);
    setNotes(value.notes.content);
    const latest = value.reviews[0];
    setDecision(latest?.decision || "");
    setComments(latest?.comments || "");
    setSuggestedRotation(latest?.suggested_rotation ? JSON.stringify(latest.suggested_rotation, null, 2) : "");
    setSoilTestRequested(Boolean(latest?.soil_test_requested));
  };
  useEffect(() => {
    let alive = true;
    Promise.all([api.expertAnalysis(id), api.crops().catch(() => [])]).then(([value, list]) => {
      if (!alive) return;
      setDetail(value); setCrops(list); setNotes(value.notes.content);
      const latest = value.reviews[0];
      setDecision(latest?.decision || ""); setComments(latest?.comments || "");
      setSuggestedRotation(latest?.suggested_rotation ? JSON.stringify(latest.suggested_rotation, null, 2) : "");
      setSoilTestRequested(Boolean(latest?.soil_test_requested));
    }).catch((reason: Error) => { if (alive) setError(reason.message); }).finally(() => { if (alive) setLoading(false); });
    return () => { alive = false; };
  }, [id]);

  const cropNames = useMemo(() => new Map(crops.map((crop) => [crop.id, crop.names.en])), [crops]);
  if (loading) return <ExpertShell><main className="expert-content"><p role="status">Loading analysis evidence…</p></main></ExpertShell>;
  if (error || !detail) return <ExpertShell><main className="expert-content"><h1>Analysis not found</h1><p className="muted" role="alert">{error || "No saved analysis exists for this ID."}</p><Button asChild variant="secondary"><Link href="/expert/dashboard"><ArrowLeft size={16} />Back to overview</Link></Button></main></ExpertShell>;

  const record: StoredAnalysis = detail.analysis;
  const result = record.result;
  const language = record.request.language || "en";
  const features = result.field_context?.environmental_features || {};
  const cluster = result.field_context?.cluster;
  const options = result.options || result.rotation_options || [];
  const seasonalHeat = objectValues(features.heat_days_40c_by_month);
  const monthlyMax = objectValues(features.tmax_mean_by_month);
  const monthlyRain = objectValues(features.rain_mm_by_month);
  const cloudFree = asNum(features.cloud_free_fraction);
  const latestReview: ExpertReview | undefined = detail.reviews[0];

  const startReview = async () => {
    setSaving(true); setError("");
    try { await api.createReview(id, { decision: null, comments: "" }); await reload(); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Could not start the review."); }
    finally { setSaving(false); }
  };
  const saveReview = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault(); setSaving(true); setError("");
    let suggested: unknown = null;
    if (suggestedRotation.trim()) {
      try { suggested = JSON.parse(suggestedRotation); }
      catch { setError("Suggested rotation must be valid JSON."); setSaving(false); return; }
      if (!Array.isArray(suggested) && (typeof suggested !== "object" || suggested === null)) {
        setError("Suggested rotation must be a JSON object or list."); setSaving(false); return;
      }
    }
    const payload = { decision: decision ? decision as ExpertReview["decision"] : null, comments,
      suggested_rotation: suggested as ExpertReview["suggested_rotation"], soil_test_requested: soilTestRequested };
    try {
      if (latestReview) await api.updateReview(latestReview.review_id, payload);
      else await api.createReview(id, payload);
      await reload(); setSaved(true); window.setTimeout(() => setSaved(false), 1800);
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Could not save the review."); }
    finally { setSaving(false); }
  };
  const saveNotes = async () => {
    setSaving(true); setError("");
    try { await api.saveExpertNotes(id, notes); setSaved(true); window.setTimeout(() => setSaved(false), 1800); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Could not save notes."); }
    finally { setSaving(false); }
  };

  return <ExpertShell><main className="expert-content">
    <header className="expert-top"><div><Link href="/expert/dashboard" className="mb-1 inline-flex min-h-11 items-center gap-1 text-sm font-semibold text-slate-600"><ArrowLeft size={15} />Overview</Link><h1>Analysis detail</h1><p>{record.analysis_id} · {formatDate(record.request.created_at)}</p></div><Badge tone={result.data_mode === "REAL" ? "green" : "amber"}>{result.data_mode || "—"}</Badge></header>
    {error && <div className="expert-block mb-4 text-sm text-red-800" role="alert">{error}</div>}
    <section className="expert-block"><div className="expert-block-head"><div><h2>Farmer inputs</h2><p className="field-help">Answers recorded with the original request.</p></div><MapPin size={17} color="#166534" /></div><Evidence rows={[
      ["Current crop", cropNames.get(record.request.current_crop) || record.request.current_crop],
      ["Previous crop", record.request.previous_crop ? cropNames.get(record.request.previous_crop) || record.request.previous_crop : "Not provided"],
      ["Water source / availability", `${record.request.water_source} · ${record.request.water_level}`],
      ["Salinity", record.request.salinity], ["Waterlogging", record.request.waterlogging],
      ["Farmer priority", record.request.priority], ["Language", record.request.language],
      ["Location", `${record.request.latitude.toFixed(5)}, ${record.request.longitude.toFixed(5)}`],
    ]} /></section>

    {result.status === "ok" && <div className="expert-detail-grid mt-4">
      <div className="detail-stack">
        <section className="expert-block"><div className="expert-block-head"><div><h2>Field location & layers</h2><p className="field-help">Selected point and validated spatial layers.</p></div><MapPin size={17} color="#166534" /></div><AppMap mode="layers" selectedPoint={{ lat: record.request.latitude, lon: record.request.longitude }} layerOpacity={layerOpacity} showAnalysisRadius labels={{ base: t(language, "baseMap"), ndvi: t(language, "ndvi"), ndmi: t(language, "ndmi"), bsi: t(language, "bsi"), slope: t(language, "slope"), layers: t(language, "layers") }} ariaLabel="Expert field evidence map" /><div className="analysis-detail-controls">
          <label className="analysis-opacity-control" htmlFor="expert-layer-opacity"><span>{t(language, "layerOpacity")}</span><input id="expert-layer-opacity" type="range" min="20" max="100" step="5" value={Math.round(layerOpacity * 100)} onChange={(event) => setLayerOpacity(Number(event.target.value) / 100)} aria-label={t(language, "layerOpacity")} /><span className="analysis-opacity-value ltr-token">{Math.round(layerOpacity * 100)}%</span></label>
          <span className="analysis-radius-help"><span className="analysis-radius-key" aria-hidden="true" /><span>{t(language, "analysisRadius")}</span><button type="button" className="analysis-radius-tip" aria-label={t(language, "radiusTooltip")} aria-describedby="analysis-radius-tooltip" title={t(language, "radiusTooltip")}><CircleHelp size={18} /><span id="analysis-radius-tooltip" className="analysis-radius-tooltip" role="tooltip">{t(language, "radiusTooltip")}</span></button></span>
        </div><div className="mt-2 flex flex-wrap justify-between gap-2 text-xs text-slate-600"><span>{result.feature_point_id || "Feature point unavailable"}</span><span>{number(result.feature_point?.distance_m, 0)} m · nearest analysis point</span></div></section>
        <section className="expert-block"><div className="expert-block-head"><div><h2>Environmental evidence</h2><p className="field-help">Values returned from the nearest validated point.</p></div><Satellite size={17} color="#166534" /></div><Evidence rows={[
          ["NDVI · Landsat 9", asNum(features.ndvi_mean) === undefined ? "—" : number(asNum(features.ndvi_mean))],
          ["NDMI · Landsat 9", asNum(features.ndmi_mean) === undefined ? "—" : number(asNum(features.ndmi_mean))],
          ["Bare-soil index", asNum(features.bsi_mean) === undefined ? "—" : number(asNum(features.bsi_mean))],
          ["Surface temperature", asNum(features.surface_temp_c) === undefined ? "—" : `${number(asNum(features.surface_temp_c), 1)} °C`],
          ["Slope", asNum(features.slope_deg) === undefined ? "—" : `${number(asNum(features.slope_deg), 1)}°`],
          ["Elevation", asNum(features.elevation_m) === undefined ? "—" : `${number(asNum(features.elevation_m), 1)} m`],
          ["Cloud-free fraction", cloudFree === undefined ? "—" : `${number(cloudFree * 100, 0)}%`],
        ]} /></section>
      </div>
      <div className="detail-stack">
        <section className="expert-block"><div className="expert-block-head"><div><h2>K-Means environmental cluster</h2><p className="field-help">{t(language, "clusterDescription")}</p></div><Badge tone="blue">Environmental grouping</Badge></div><div className="cluster-name">{cluster?.cluster_label ? localizedClusterLabel(language, cluster.cluster_label) : t(language, "clusterUnavailable")}</div><Evidence rows={[["Cluster ID", cluster?.cluster_id === undefined ? "—" : String(cluster.cluster_id)], ["Model", result.model_metadata?.name || "—"], ["Version", result.model_metadata?.version || "—"], ["Status", result.model_metadata?.status || "—"]]} /></section>
        <section className="expert-block"><div className="expert-block-head"><div><h2>Climate summary</h2><p className="field-help">Monthly arrays are shown only when returned.</p></div></div><MonthlyBars title="Mean maximum temperature" values={monthlyMax} unit="°C" /><MonthlyBars title="Rain history" values={monthlyRain} unit="mm" /><MonthlyBars title="Days at or above 40°C" values={seasonalHeat} unit="days" />{!monthlyMax.length && !monthlyRain.length && !seasonalHeat.length && <p className="text-sm text-slate-600">No monthly climate values were returned.</p>}<p className="mt-3 text-xs text-slate-500">Temporal alignment: {result.temporal_alignment || "not returned"} · Regional context: {result.regional_context_status || "not returned"}</p></section>
      </div>
    </div>}

    {result.status !== "ok" && <div className="expert-block mt-4"><Badge tone="amber">{result.status}</Badge><p className="mb-0 mt-3">No supported environmental rotation result was generated for this analysis.</p></div>}
    <section className="expert-block mt-4"><div className="expert-block-head"><div><h2>Dataset dates and resolutions</h2><p className="field-help">Source metadata saved with the farmer analysis.</p></div><CheckCircle2 size={17} color="#166534" /></div><Evidence rows={[
      ["Landsat 9", `${result.dataset_metadata?.landsat_9?.observation_date || result.data_snapshot?.landsat_date || "Date unavailable"} · ${formatResolution(result.dataset_metadata?.landsat_9?.resolution)}`],
      ["SRTM", `${result.dataset_metadata?.srtm?.observation_date || "Date unavailable"} · ${formatResolution(result.dataset_metadata?.srtm?.resolution)}`],
      ["NASA POWER", `${result.dataset_metadata?.nasa_power?.period || "Period unavailable"} · ${formatResolution(result.dataset_metadata?.nasa_power?.resolution)}`],
      ["Forecast status", forecastStatus(result)], ["Regional context", result.regional_context_status || "Unavailable"],
    ]} /></section>

    <section className="expert-block mt-4"><div className="expert-block-head"><div><h2>Three rotation options and score breakdown</h2><p className="field-help">Factor values are diagnostics; adjustments and final score follow the existing rule engine.</p></div><Badge tone="neutral">{options.length} options</Badge></div>
      {options.length ? options.map((option) => <article className="option-review" key={option.id}>
        <div className="flex items-start justify-between gap-3"><div><strong>{option.id === "existing" ? "Existing rotation" : option.id === "balanced" ? "Balanced alternative" : "Farmer-priority alternative"}</strong><div className="mt-1 text-xs text-slate-600">{option.seasons.map((item) => `${item.season}: ${cropNames.get(item.crop) || item.crop}`).join(" → ")}</div></div><strong>{option.score}/100</strong></div>
        <div className="score-bar mt-2"><span style={{ width: `${Math.max(0, Math.min(100, option.score))}%` }} /></div>
        <div className="mt-2 flex flex-wrap gap-2"><Badge tone={option.light === "red" ? "red" : option.light === "yellow" ? "amber" : "green"}>{option.light}</Badge><Badge tone={option.crop_verified ? "green" : "amber"}>{option.crop_verified ? "Rules verified" : "Rules unverified"}</Badge>{option.expert_needed && <Badge tone="amber">Review advised</Badge>}</div>
        {(option.warnings || []).map((warning, index) => <p className="mt-2 text-xs text-amber-900" key={index}><AlertTriangle size={14} className="mr-1 inline" />{warning}</p>)}
        <div className="score-components">{Object.entries(detail.score_breakdown[option.id] || {}).map(([key, component]) => <ScoreRow key={key} label={componentLabels[key] || key} component={component} />)}</div>
      </article>) : <p className="text-sm text-slate-600">No rotation options were generated for this analysis.</p>}
      {result.limitations?.length ? <ul className="mt-4 list-disc space-y-1 pl-5 text-xs leading-5 text-slate-600">{result.limitations.map((item) => <li key={item}>{item}</li>)}</ul> : null}
    </section>

    <section className="expert-block mt-4"><div className="expert-block-head"><div><h2>Review status and actions</h2><p className="field-help">Review decisions are saved with the authenticated expert and audit timestamps.</p></div><Badge tone={detail.review_status === "approved" ? "green" : detail.review_status === "not_reviewed" || detail.review_status === "under_review" ? "amber" : "blue"}>{reviewLabels[detail.review_status]}</Badge></div>
      {detail.review_status === "not_reviewed" && !latestReview && <Button variant="secondary" disabled={saving} onClick={startReview}><ClipboardCheck size={15} />Start review</Button>}
      {(detail.review_status !== "not_reviewed" || latestReview) && <form className="review-form" onSubmit={saveReview}>
        <label><span>Decision</span><select value={decision} onChange={(event) => setDecision(event.target.value)}><option value="">Keep under review</option>{decisionOptions.map((item) => <option key={item} value={item}>{reviewLabels[item]}</option>)}</select></label>
        <label><span>Comments</span><Textarea value={comments} onChange={(event) => setComments(event.target.value)} aria-label="Review comments" placeholder="Add expert findings or follow-up needed…" /></label>
        <label><span>Suggested rotation (optional JSON)</span><Textarea value={suggestedRotation} onChange={(event) => setSuggestedRotation(event.target.value)} aria-label="Suggested rotation" placeholder='[{"season":"rabi","crop":"wheat"}]' /></label>
        <label className="review-checkbox"><input type="checkbox" checked={soilTestRequested} onChange={(event) => setSoilTestRequested(event.target.checked)} />Request a soil test</label>
        <Button type="submit" disabled={saving}>{saving ? "Saving…" : "Save review"}</Button>
      </form>}
      <h3 className="mt-5 font-semibold">Review history</h3>{detail.reviews.length ? <div className="analysis-list">{detail.reviews.map((review) => <article className="analysis-list-row review-history-row" key={review.review_id}><div><strong>{review.decision ? reviewLabels[review.decision] : "Review started"}</strong><p className="mb-0 mt-1 text-xs text-slate-600">{review.comments || "No comments"}</p>{review.soil_test_requested && <small>Soil test requested</small>}</div><span>{formatDate(review.reviewed_at || review.created_at)}</span></article>)}</div> : <p className="text-sm text-slate-600">No reviews recorded.</p>}
    </section>

    <section className="expert-block mt-4"><div className="expert-block-head"><div><h2>Expert notes</h2><p className="field-help">Notes are stored on the server for this analysis.</p></div><ClipboardCheck size={17} color="#166534" /></div><Textarea value={notes} onChange={(event) => setNotes(event.target.value)} aria-label="Expert notes" placeholder="Record local observations or follow-up needed…" /><Button variant="soft" className="mt-3" onClick={saveNotes} disabled={saving}><Save size={15} />{saved ? "Saved" : "Save notes"}</Button><p className="mt-2 text-xs text-slate-500">Updated: {detail.notes.updated_at ? formatDate(detail.notes.updated_at) : "Not saved yet"}</p></section>
  </main></ExpertShell>;
}

function ScoreRow({ label, component }: { label: string; component: ScoreComponent }) {
  return <div className="score-component-row"><span><strong>{label}</strong><small>{component.reason}</small><small>{component.rule_id} · {component.verified ? "Verified" : "Unverified"} · {component.source}</small></span><strong>{number(component.value, 2)}</strong></div>;
}
function Evidence({ rows }: { rows: [string, string][] }) { return <div className="evidence-list">{rows.map(([label, value]) => <div key={label} className="evidence-row"><span>{label}</span><strong>{value}</strong></div>)}</div>; }
function objectValues(value: unknown) { if (!value || typeof value !== "object" || Array.isArray(value)) return []; return Object.entries(value).map(([month, amount]) => ({ month: Number(month), value: asNum(amount) })).filter((item): item is { month: number; value: number } => Number.isFinite(item.month) && item.value !== undefined).sort((a, b) => a.month - b.month); }
function MonthlyBars({ title, values, unit }: { title: string; values: { month: number; value: number }[]; unit: string }) {
  if (!values.length) return null;
  const max = Math.max(...values.map((item) => item.value), 0.001);
  return <div className="month-chart"><div className="mb-2 flex items-center justify-between"><strong>{title}</strong><span>{unit}</span></div><div className="month-bars">{values.map((item) => <div className="month-bar-item" key={item.month} title={`${monthName(item.month)}: ${number(item.value)} ${unit}`}><div className="month-bar-track"><span style={{ height: `${Math.max(2, item.value / max * 100)}%` }} /></div><small>{monthName(item.month).slice(0, 3)}</small></div>)}</div></div>;
}
function monthName(month: number) { return new Intl.DateTimeFormat("en", { month: "short" }).format(new Date(2026, month - 1, 1)); }
function formatResolution(value: unknown) { return typeof value === "number" ? `${value} m` : value ? String(value) : "Resolution unavailable"; }
function forecastStatus(result: StoredAnalysis["result"]) { const forecast = result.forecast; return forecast?.is_live ? "Live" : forecast?.is_sample ? forecast.expired ? "Expired saved sample" : "Saved sample" : "Unavailable"; }
