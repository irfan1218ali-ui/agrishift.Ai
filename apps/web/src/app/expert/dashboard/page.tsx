"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { ArrowRight, Clock3, Database, Search, ShieldCheck } from "lucide-react";
import { ExpertShell } from "@/components/expert-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import { formatDate, number } from "@/lib/utils";
import type { ExpertAnalysisList, ExpertSummary, Health, LayerCatalog, StoredAnalysis } from "@/lib/types";

type Filters = { status: string; confidence: string; previous_crop: string; priority: string; salinity: string; waterlogging: string; date_from: string; date_to: string; search: string };
const emptyFilters: Filters = { status: "", confidence: "", previous_crop: "", priority: "", salinity: "", waterlogging: "", date_from: "", date_to: "", search: "" };
const statusText: Record<string, string> = { not_reviewed: "Not reviewed", under_review: "Under review", approved: "Approved", approved_with_changes: "Approved with changes", needs_more_information: "Needs more information", unsuitable: "Unsuitable" };

export default function ExpertDashboardPage() {
  const [health, setHealth] = useState<Health | null>(null);
  const [layers, setLayers] = useState<LayerCatalog | null>(null);
  const [summary, setSummary] = useState<ExpertSummary | null>(null);
  const [list, setList] = useState<ExpertAnalysisList | null>(null);
  const [filters, setFilters] = useState<Filters>(emptyFilters);
  const [activeFilters, setActiveFilters] = useState<Filters>(emptyFilters);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let alive = true;
    Promise.all([api.health().catch(() => null), api.layers().catch(() => null), api.expertSummary()])
      .then(([status, catalog, totals]) => { if (alive) { setHealth(status); setLayers(catalog); setSummary(totals); } })
      .catch((reason: Error) => { if (alive) setError(reason.message); });
    return () => { alive = false; };
  }, []);

  useEffect(() => {
    let alive = true;
    setLoading(true);
    const query = new URLSearchParams({ page: String(page), page_size: "12" });
    for (const [key, value] of Object.entries(activeFilters)) if (value.trim()) query.set(key, value.trim());
    api.expertAnalyses(query).then((value) => { if (alive) setList(value); })
      .catch((reason: Error) => { if (alive) setError(reason.message); })
      .finally(() => { if (alive) setLoading(false); });
    return () => { alive = false; };
  }, [page, activeFilters]);

  const applyFilters = (event: FormEvent<HTMLFormElement>) => { event.preventDefault(); setPage(1); setActiveFilters({ ...filters }); };
  const layerRows = layers ? Object.entries(layers.layers).map(([id, layer]) => ({ id, ...layer })) : [];
  const records = list?.items || [];
  const recent = summary?.recent_analyses || [];
  const dataStatus = health?.features_available ? health.environmental_clustering === "available" ? "Ready" : "Partial" : "Unavailable";

  return <ExpertShell><main className="expert-content">
    <header className="expert-top"><div><p className="section-kicker">AgriShift AI · Hyderabad pilot</p><h1>Expert overview</h1><p>Review analysis evidence and flag rotations that need local agronomic attention.</p></div><Button asChild><Link href="/analyze"><ArrowRight size={16} />Start farmer flow</Link></Button></header>
    {error && <div className="expert-block mb-4 text-sm text-amber-900" role="alert">Expert data could not be loaded: {error}</div>}
    <div className="expert-block flex flex-wrap items-center justify-between gap-4"><div><div className="flex items-center gap-2"><Database size={17} color="#166534" /><h2>Workspace data</h2></div><p className="mb-0 mt-1 text-sm text-slate-600">Global farmer analyses and review status loaded from the backend.</p></div><Badge tone={health?.data_mode === "REAL" ? "green" : health?.data_mode === "DEMO" ? "amber" : "neutral"}>{health?.data_mode ? `${health.data_mode} DATA` : "DATA UNAVAILABLE"}</Badge></div>
    <section className="expert-stat-grid" aria-label="Analysis statistics">
      <Stat label="Total analyses" value={summary ? String(summary.total_analyses) : "—"} note="Saved farmer requests" />
      <Stat label="Pending reviews" value={summary ? String(summary.pending_reviews) : "—"} note="Not reviewed or in progress" />
      <Stat label="Low confidence" value={summary ? String(summary.low_confidence_analyses) : "—"} note="Below 55 confidence points" />
      <Stat label="Completed reviews" value={summary ? String(summary.completed_reviews) : "—"} note="Decision recorded by expert" />
    </section>

    <div className="expert-grid">
      <section id="analyses" className="expert-block">
        <div className="expert-block-head"><div><h2>All analyses</h2><p className="field-help">Filter and page through every saved farmer request.</p></div><span className="eyebrow">{list ? `${list.total} total` : "Loading"}</span></div>
        <form className="expert-filters" onSubmit={applyFilters}>
          <label><span>Search</span><input className="expert-filter-input" value={filters.search} onChange={(event) => setFilters({ ...filters, search: event.target.value })} placeholder="Analysis ID or crop" /><Search size={15} /></label>
          <label><span>Review status</span><select className="expert-filter-input" value={filters.status} onChange={(event) => setFilters({ ...filters, status: event.target.value })}><option value="">All statuses</option>{Object.entries(statusText).map(([value, label]) => <option value={value} key={value}>{label}</option>)}</select></label>
          <label><span>Confidence</span><select className="expert-filter-input" value={filters.confidence} onChange={(event) => setFilters({ ...filters, confidence: event.target.value })}><option value="">All confidence</option><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option></select></label>
          <label><span>Previous crop</span><input className="expert-filter-input" value={filters.previous_crop} onChange={(event) => setFilters({ ...filters, previous_crop: event.target.value })} placeholder="e.g. wheat" /></label>
          <label><span>Priority</span><select className="expert-filter-input" value={filters.priority} onChange={(event) => setFilters({ ...filters, priority: event.target.value })}><option value="">Any priority</option><option value="save_water">Save water</option><option value="improve_soil">Improve soil</option><option value="balanced">Balanced</option></select></label>
          <label><span>Salinity</span><select className="expert-filter-input" value={filters.salinity} onChange={(event) => setFilters({ ...filters, salinity: event.target.value })}><option value="">Any</option><option value="yes">Yes</option><option value="no">No</option><option value="unknown">Unknown</option></select></label>
          <label><span>Waterlogging</span><select className="expert-filter-input" value={filters.waterlogging} onChange={(event) => setFilters({ ...filters, waterlogging: event.target.value })}><option value="">Any</option><option value="yes">Yes</option><option value="no">No</option><option value="unknown">Unknown</option></select></label>
          <label><span>From</span><input className="expert-filter-input" type="date" value={filters.date_from} onChange={(event) => setFilters({ ...filters, date_from: event.target.value })} /></label>
          <label><span>To</span><input className="expert-filter-input" type="date" value={filters.date_to} onChange={(event) => setFilters({ ...filters, date_to: event.target.value })} /></label>
          <Button type="submit">Apply filters</Button><Button type="button" variant="secondary" onClick={() => { setFilters(emptyFilters); setActiveFilters(emptyFilters); setPage(1); }}>Clear</Button>
        </form>
        {loading ? <p className="text-sm text-slate-600" role="status">Loading analyses…</p> : records.length === 0 ? <div className="empty-frame"><p>No analyses match these filters.</p></div> : <div className="analysis-list">
          <div className="analysis-list-row header"><span>Analysis</span><span>Created</span><span>Confidence</span><span>Review status</span></div>
          {records.map((record) => <AnalysisRow key={record.analysis_id} record={record} />)}
        </div>}
        {list && <div className="mt-4 flex items-center justify-between gap-3 text-sm"><span>Page {list.page} of {Math.max(1, list.total_pages)}</span><div className="flex gap-2"><Button variant="secondary" disabled={page <= 1} onClick={() => setPage((value) => value - 1)}>Previous</Button><Button variant="secondary" disabled={page >= list.total_pages} onClick={() => setPage((value) => value + 1)}>Next</Button></div></div>}
      </section>
      <section className="expert-block">
        <div className="expert-block-head"><div><h2>Dataset readiness</h2><p className="field-help">Evidence source dates and resolutions.</p></div><Clock3 size={17} color="#607080" /></div>
        <div className="flex items-center justify-between border-b border-slate-100 py-2 text-xs"><span className="text-slate-600">Feature points</span><strong>{health?.features_available ? "Available" : health ? "Unavailable" : "—"}</strong></div>
        <div className="flex items-center justify-between border-b border-slate-100 py-2 text-xs"><span className="text-slate-600">K-Means model</span><strong>{health?.environmental_clustering || "—"}</strong></div>
        <div className="freshness-list">{layerRows.map((layer) => <div className="freshness-row" key={layer.id}><span>{layerNames[layer.id] || layer.id.toUpperCase()}</span><strong>{layer.observation_date} · {layer.source_resolution_m} m</strong></div>)}</div>
        {layerRows.length === 0 && <p className="text-sm text-slate-500">Layer metadata could not be loaded.</p>}
        <div className="mt-3 text-xs text-slate-600">Data/model status: <strong>{dataStatus}</strong></div>
      </section>
    </div>

    <section className="expert-block mt-4">
      <div className="expert-block-head"><div><div className="flex items-center gap-2"><ShieldCheck size={17} color="#166534" /><h2>Recent analyses</h2></div><p className="field-help">Most recently saved farmer requests.</p></div><Badge tone="neutral">{recent.length} recent</Badge></div>
      {recent.length ? <div className="analysis-list"><div className="analysis-list-row header"><span>Analysis</span><span>Created</span><span>Confidence</span><span>Review status</span></div>{recent.map((record) => <AnalysisRow key={record.analysis_id} record={record} />)}</div> : <div className="empty-frame"><p>No analyses have been saved yet.</p><Button asChild variant="soft"><Link href="/analyze">Run farmer analysis <ArrowRight size={15} /></Link></Button></div>}
    </section>
  </main></ExpertShell>;
}

function AnalysisRow({ record }: { record: StoredAnalysis }) {
  const review = record.review_status || "not_reviewed";
  const tone = review === "approved" ? "green" : review === "not_reviewed" || review === "under_review" ? "amber" : "blue";
  return <div className="analysis-list-row"><Link className="analysis-link" href={`/expert/analysis/${encodeURIComponent(record.analysis_id)}`}>{record.request.current_crop.replaceAll("_", " ")} · {record.analysis_id.slice(0, 8)}</Link><span>{formatDate(record.request.created_at)}</span><span>{number(record.result.confidence?.score, 0)}%</span><span><Badge tone={tone}>{statusText[review] || review}</Badge></span></div>;
}

function Stat({ label, value, note }: { label: string; value: string; note: string }) {
  return <article className="expert-stat"><span>{label}</span><strong>{value}</strong><small>{note}</small></article>;
}

const layerNames: Record<string, string> = { ndvi: "Vegetation", ndmi: "Moisture", bsi: "Bare soil", slope: "Slope" };
