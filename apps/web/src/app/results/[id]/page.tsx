"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";
import { AlertTriangle, ArrowLeft, ArrowRight, Check, CheckCircle2, Cloud, Droplets, ExternalLink, Leaf, Map as MapIcon, MapPin, Satellite, Share2, ShieldCheck, Sprout, ThermometerSun, Waves } from "lucide-react";
import { AppMap } from "@/components/app-map";
import { Brand } from "@/components/brand";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import { direction, explain, localizedClusterLabel, tf, t } from "@/lib/i18n";
import { formatDate, number } from "@/lib/utils";
import type { Crop, Language, RotationOption, StoredAnalysis } from "@/lib/types";

const langTag: Record<Language, string> = { en: "en-PK", ur: "ur-PK", sd: "sd-PK" };
const asNumber = (value: unknown): number | undefined => typeof value === "number" && Number.isFinite(value) ? value : undefined;
const titleFor = (id: string, language: Language) => id === "existing" ? t(language, "current") : id === "balanced" ? t(language, "balancedOption") : t(language, "priorityOption");
const iconFor = (index: number) => index === 0 ? Leaf : index === 1 ? Sprout : Droplets;

export default function ResultsPage() {
  const params = useParams<{ id: string }>();
  const id = decodeURIComponent(params.id || "");
  const [record, setRecord] = useState<StoredAnalysis | null>(null);
  const [crops, setCrops] = useState<Crop[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<"missing" | "unavailable" | "">("");
  const [lang, setLang] = useState<Language>("en");

  useEffect(() => {
    let alive = true;
    Promise.all([api.analysis(id), api.crops().catch(() => [])]).then(([saved, cropList]) => {
      if (!alive) return;
      setRecord(saved); setCrops(cropList);
      const selected = saved.request.language || "en";
      setLang(selected);
      document.documentElement.lang = selected;
      document.documentElement.dir = direction(selected);
    }).catch((reason: Error) => { if (alive) setError(/not found/i.test(reason.message) ? "missing" : "unavailable"); }).finally(() => { if (alive) setLoading(false); });
    return () => { alive = false; };
  }, [id]);

  const result = record?.result;
  const options = result?.options || result?.rotation_options || [];
  const cropById = useMemo(() => new Map(crops.map((crop) => [crop.id, crop])), [crops]);
  const cropName = (cropId: string) => cropById.get(cropId)?.names[lang] || cropId;
  const features = result?.field_context?.environmental_features || {};
  const cluster = result?.field_context?.cluster;
  const forecast = result?.forecast || result?.weather;
  const sourceDates = result?.data_snapshot?.source_dates || {};
  const sourceResolution = result?.data_snapshot?.source_resolutions || {};

  useEffect(() => {
    if (!record) return;
    document.documentElement.lang = record.request.language || "en";
    document.documentElement.dir = direction(record.request.language || "en");
  }, [record]);

  if (loading) return <main className="result-page frame" role="status"><Brand href="/" /><div className="wizard-panel mt-6"><div className="spinner" /><p>{t(lang, "loading")}</p></div></main>;
  if (error || !record || !result) return <main className="result-page frame"><Brand href="/" /><div className="wizard-panel mt-6" role="alert"><h1>{error === "unavailable" ? t(lang, "analysisUnavailable") : t(lang, "analysisMissing")}</h1><Button asChild className="mt-4"><Link href="/analyze">{t(lang, "retry")}</Link></Button></div></main>;

  const failureText = result.status === "not_applicable" ? t(lang, "unsupported") : result.status === "insufficient_data" ? t(lang, "insufficient") : "";
  const overallConfidence = result.confidence?.score;
  const distance = result.feature_point?.distance_m;
  const clusterName = localizedClusterLabel(lang, cluster?.cluster_label || result.field_context?.cluster_label || "—");
  const reviewStatus = record.review_status || "not_reviewed";
  const reviewStatusKeys = { not_reviewed: "reviewNotReviewed", under_review: "reviewUnderReview", approved: "reviewApproved", approved_with_changes: "reviewApprovedChanges", needs_more_information: "reviewNeedsInfo", unsuitable: "reviewUnsuitable" } as const;
  const reportDate = formatDate(record.request.created_at, langTag[lang]);
  const soilBenefit = (option: RotationOption) => {
    const ids = option.why_ids || [];
    if (ids.includes("why_legume_001") || ids.includes("why_soil_help_001")) return t(lang, "soilBenefitLegume");
    return t(lang, "soilBenefitNone");
  };
  const riskText = (option: RotationOption) => option.light === "red" ? t(lang, "riskNeedsAttention") : option.light === "yellow" ? t(lang, "riskReviewCautions") : t(lang, "riskFewerFlagged");
  const shareSummary = `AgriShift AI field analysis ${record.analysis_id}\n${options.map((option) => `${titleFor(option.id, lang)}: ${option.seasons.map((season) => cropName(season.crop)).join(" → ")} · ${option.score}/100`).join("\n")}\nExpert review may be needed.`;
  const bestActions = [
    ...(!options.every((option) => option.crop_verified) ? [t(lang, "unverifiedRuleWarning")] : []),
    ...(record.request.salinity === "yes" ? ["Inspect salt signs and consider a local soil test."] : []),
    ...(record.request.waterlogging === "yes" ? ["Check field drainage before the next sowing."] : []),
    "Confirm seed availability for the selected crops.",
    "Check sowing dates with a local agriculture advisor.",
    "Confirm current local market demand; market value was not assessed.",
  ].slice(0, 5);
  const datasetRows = [
    ["Landsat 9", result.dataset_metadata?.landsat_9?.observation_date || sourceDates.landsat_9 || result.data_snapshot?.landsat_date, result.dataset_metadata?.landsat_9?.resolution || sourceResolution.landsat_9 || "—"],
    ["SRTM terrain", result.dataset_metadata?.srtm?.observation_date || sourceDates.srtm_dem, result.dataset_metadata?.srtm?.resolution || sourceResolution.srtm_dem || "—"],
    ["NASA POWER", result.dataset_metadata?.nasa_power?.period || sourceDates.nasa_power_climate, result.dataset_metadata?.nasa_power?.resolution || sourceResolution.nasa_power_climate || "—"],
  ];

  return (
    <main className="result-page frame" lang={lang} dir={direction(lang)}>
      <header className="mb-5 flex items-center justify-between gap-3">
        <Brand href="/" /><Link href="/expert/login" className="inline-flex min-h-11 items-center gap-2 rounded-xl px-3 text-sm font-semibold text-slate-600 hover:bg-slate-100">{t(lang, "expert")}<ArrowRight size={15} className="rtl-flip" /></Link>
      </header>
      <div className="expert-review-status" role="status"><strong>{t(lang, "reviewStatus")}</strong><Badge tone={reviewStatus === "approved" ? "green" : reviewStatus === "not_reviewed" || reviewStatus === "under_review" ? "amber" : "blue"}>{t(lang, reviewStatusKeys[reviewStatus])}</Badge></div>
      {failureText ? <section className="wizard-panel" role="alert"><Badge tone={result.status === "not_applicable" ? "amber" : "red"}>{result.status === "not_applicable" ? "Not applicable" : "Insufficient data"}</Badge><h1 className="mt-3 text-2xl font-semibold">{failureText}</h1><p className="muted mt-2">No rotation scores or crop recommendations were generated for this location.</p><div className="result-meta mt-4"><span><MapPin size={15} /><span className="ltr-token">{record.request.latitude.toFixed(4)}, {record.request.longitude.toFixed(4)}</span></span><span>{t(lang, "analysisId")}: <span className="ltr-token">{record.analysis_id}</span></span></div><Button asChild className="mt-5"><Link href="/analyze">{t(lang, "retry")}</Link></Button></section> : <>
        <section className="result-hero">
          <div>
            <Badge tone={result.data_mode === "DEMO" ? "amber" : "green"}><span className="dot" />{result.data_mode === "DEMO" ? t(lang, "demo") : t(lang, "real")}</Badge>
            <h1>{t(lang, "results")}</h1>
            <div className="result-meta">
              <span><MapPin size={15} />Hyderabad pilot field point</span>
              <span>{t(lang, "distance")}: <span className="ltr-token">{distance === undefined ? "—" : distance < 1000 ? `${number(distance, 0)} m` : `${number(distance / 1000, 2)} km`}</span></span>
              <span>{t(lang, "analysisDate")}: <span className="ltr-token">{reportDate}</span></span>
            </div>
            <p className="mt-4 text-sm text-slate-600">{t(lang, "cluster")}: <strong className="text-slate-900">{clusterName}</strong></p>
          </div>
          <div className="result-confidence"><span className="eyebrow">{t(lang, "confidence")}</span><strong className="ltr-token">{overallConfidence === undefined ? "—" : `${number(overallConfidence, 0)}%`}</strong><div className="confidence-dots" aria-label={result.confidence?.dots || "Confidence not returned"}>{result.confidence?.dots || "—"}</div></div>
        </section>
        {options.some((option) => option.expert_needed || !option.crop_verified) && <div className="expert-warning" role="note"><AlertTriangle size={19} /><div><strong>{t(lang, "expertReview")}</strong><div>{t(lang, "unverifiedRuleWarning")}</div></div></div>}

        <section className="result-section">
          <div className="result-section-heading"><h2>{t(lang, "environmental")}</h2><span className="eyebrow ltr-token">Landsat 9 · {result.data_snapshot?.landsat_date || "—"}</span></div>
          <div className="metric-grid">
            <Metric icon={<Leaf size={17} />} label={t(lang, "vegetation")} value={clusterName} sub={t(lang, "clusterDescription")} />
            <Metric icon={<Waves size={17} />} label={t(lang, "moisture")} value={asNumber(features.ndmi_mean) === undefined ? "—" : number(asNumber(features.ndmi_mean))} sub="NDMI · 30 m source layer" ltrValue />
            <Metric icon={<ThermometerSun size={17} />} label={t(lang, "surfaceHeat")} value={asNumber(features.surface_temp_c) === undefined ? "—" : `${number(asNumber(features.surface_temp_c), 1)} °C`} sub="Landsat surface observation" ltrValue />
            <Metric icon={<MapIcon size={17} />} label={t(lang, "terrain")} value={asNumber(features.slope_deg) === undefined ? "—" : `${number(asNumber(features.slope_deg), 1)}°`} sub="SRTM slope · 30 m" ltrValue />
          </div>
        </section>

        <section className="result-section">
          <div className="result-section-heading"><h2>{t(lang, "comparison")}</h2><span className="eyebrow">{t(lang, "sequenceCount")}</span></div>
          <div className="rotation-grid">
            {options.slice(0, 3).map((option, index) => {
              const Icon = iconFor(index);
              const featured = option.id === "balanced";
              const reasonItems = (option.why_ids || []).map((reason) => explain(lang, reason));
              const cautionItems = [...(option.caution_ids || []), ...(option.warning_ids || [])].map((reason) => explain(lang, reason));
              const confidenceDots = Math.max(0, Math.min(3, option.confidence_dots || 0));
              return <article className={`rotation-card ${featured ? "featured" : ""}`} key={option.id}>
                <div className="rotation-head"><h3>{option.id === "priority" || option.id.includes("save") || option.id.includes("soil") ? `${t(lang, "priorityOption")}: ${t(lang, record.request.priority as "save_water" | "improve_soil" | "balanced")}` : titleFor(option.id, lang)}</h3>{featured && <Badge tone="green">{t(lang, "recommended")}</Badge>}</div>
                <div className="rotation-score">{option.score}<small> / 100 · {t(lang, "score")}</small></div>
                <div className="crop-sequence" aria-label={t(lang, "sequence")}>
                  <span><Icon size={17} /><small>{seasonLabel(option.seasons[0]?.season, lang)}</small>{cropName(option.seasons[0]?.crop || "—")}</span>
                  <ArrowRight size={17} color="#718078" />
                  <span><Icon size={17} /><small>{seasonLabel(option.seasons[1]?.season, lang)}</small>{cropName(option.seasons[1]?.crop || "—")}</span>
                </div>
                <ul className="rotation-facts">
                  <li><span>{t(lang, "waterNeed")}</span><strong className="inline-flex items-center gap-1"><Droplets size={15} /><span className="ltr-token">{Math.max(1, Math.min(3, option.water_drops || 1))}/3</span></strong></li>
                  <li><span>{t(lang, "soilBenefit")}</span><strong>{soilBenefit(option)}</strong></li>
                  <li><span>{t(lang, "risk")}</span><strong><Badge tone={option.light === "red" ? "red" : option.light === "yellow" ? "amber" : "green"}>{riskText(option)}</Badge></strong></li>
                  <li><span>{t(lang, "verified")}</span><strong>{option.crop_verified ? <Badge tone="green">{t(lang, "verified")}</Badge> : <Badge tone="amber">{t(lang, "unverified")}</Badge>}</strong></li>
                </ul>
                <div className="rotation-details"><h4>{t(lang, "benefits")}</h4>{reasonItems.length ? reasonItems.map((item, i) => <p key={i}><Check size={14} />{item}</p>) : <p><Check size={14} />{t(lang, "noBenefitDetails")}</p>}</div>
                <div className="rotation-details"><h4>{t(lang, "risks")}</h4>{cautionItems.length ? cautionItems.map((item, i) => <p key={i} className="risk-copy"><AlertTriangle size={14} />{item}</p>) : <p><ShieldCheck size={14} />{t(lang, "noAdditionalCaution")}</p>}</div>
                <div className="confidence-line"><div><strong>{t(lang, "confidence")}</strong><span className="ltr-token">{option.confidence_score === undefined ? "—" : `${number(option.confidence_score, 0)}%`}</span></div><div className="confidence-dots" aria-label={`${confidenceDots} of 3 confidence dots`}>{"●".repeat(confidenceDots)}{"○".repeat(3 - confidenceDots)}</div></div>
              </article>;
            })}
          </div>
          <p className="field-help mt-3">{t(lang, "scoreNote")}</p>
        </section>

        <section className="result-section">
          <div className="result-section-heading"><h2>{t(lang, "comparison")}</h2></div>
          <div className="comparison-wrap"><table className="comparison-table"><thead><tr><th>{t(lang, "measure")}</th>{options.slice(0, 3).map((o) => <th key={o.id}>{titleFor(o.id, lang)}</th>)}</tr></thead><tbody>
            <CompareRow label={t(lang, "waterNeed")} values={options.slice(0, 3).map((o) => `${o.water_drops}/3 ${t(lang, "drops")}`)} />
            <CompareRow label={t(lang, "soilBenefit")} values={options.slice(0, 3).map(soilBenefit)} />
            <CompareRow label={t(lang, "heatCheck")} values={options.slice(0, 3).map((o) => (o.caution_ids || []).includes("caution_heat_001") ? t(lang, "heatSeasonalCheck") : t(lang, "heatNoCaution"))} />
            <CompareRow label={t(lang, "risk")} values={options.slice(0, 3).map(riskText)} />
            <CompareRow label={t(lang, "market")} values={options.slice(0, 3).map(() => t(lang, "notAssessed"))} />
            <CompareRow label={t(lang, "expertStatus")} values={options.slice(0, 3).map((o) => o.expert_needed ? t(lang, "required") : t(lang, "notRequired"))} />
          </tbody></table></div>
        </section>

        <section className="result-section">
          <div className="result-section-heading"><div><h2>{t(lang, "weather")}</h2><p className="field-help">{t(lang, "weatherStatusHelp")}</p></div><Badge tone={forecast?.is_live ? "green" : forecast?.is_sample ? forecast.expired ? "amber" : "blue" : "neutral"}>{forecast?.is_live ? t(lang, "live") : forecast?.is_sample ? forecast.expired ? t(lang, "expired") : t(lang, "sample") : t(lang, "forecastUnavailable")}</Badge></div>
          {forecast?.available && (forecast.days || []).length > 0 ? <div className="weather-strip">{forecast.days?.map((day) => <article key={day.date} className="weather-card"><div className="weather-day ltr-token">{formatDate(day.date, langTag[lang])}</div><Cloud className="mt-2 text-slate-500" size={21} /><div className="weather-temp ltr-token">{day.tmax_c === undefined ? "—" : `${number(day.tmax_c, 0)}°`}<span className="ml-1 text-sm font-medium text-slate-500">/ {day.tmin_c === undefined ? "—" : `${number(day.tmin_c, 0)}°`}</span></div><div className="weather-stats"><span>{t(lang, "weatherRain")} · <span className="ltr-token">{day.rain_total_mm === undefined ? "—" : `${number(day.rain_total_mm, 1)} mm`}</span></span><span>{t(lang, "weatherHumidity")} · <span className="ltr-token">{day.rh_mean === undefined ? "—" : `${number(day.rh_mean, 0)}%`}</span></span><span>{t(lang, "weatherWind")} · <span className="ltr-token">{day.wind_max_ms === undefined ? "—" : `${number(day.wind_max_ms, 1)} m/s`}</span></span></div></article>)}</div> : <div className="wizard-panel py-4"><p className="m-0 text-sm text-slate-600">{forecast?.expired ? t(lang, "forecastExpiredContinue") : t(lang, "forecastUnavailableContinue")}</p></div>}
        </section>

        <section className="result-section">
          <div className="result-section-heading"><div><h2>{t(lang, "map")}</h2><p className="field-help">Real layer image bounds load from the API metadata.</p></div><Badge tone="neutral">{result.feature_point_id || "Environmental point"}</Badge></div>
          <div className="map-result"><AppMap mode="layers" selectedPoint={{ lat: record.request.latitude, lon: record.request.longitude }} className="result-map" labels={{ base: t(lang, "baseMap"), ndvi: t(lang, "ndvi"), ndmi: t(lang, "ndmi"), bsi: t(lang, "bsi"), slope: t(lang, "slope"), layers: t(lang, "layers") }} ariaLabel={t(lang, "map")} /><div className="map-meta"><span>{t(lang, "distance")}: <span className="ltr-token">{distance === undefined ? "—" : `${number(distance, 0)} m`}</span></span><span className="ltr-token">NDVI · NDMI · BSI · Slope</span></div></div>
        </section>

        <section className="result-section">
          <div className="result-section-heading"><h2>{t(lang, "whyThis")}</h2></div>
          <div className="why-timeline">
            <WhyStep icon={<MapPin size={18} />} title={t(lang, "timelinePointTitle")} detail={distance === undefined ? t(lang, "timelinePointMissing") : tf(lang, "timelinePointDetail", { id: result.feature_point_id || "Feature point", distance: number(distance, 0) })} />
            <WhyStep icon={<Satellite size={18} />} title={t(lang, "timelineSatelliteTitle")} detail={tf(lang, "timelineSatelliteDetail", { date: result.data_snapshot?.landsat_date || t(lang, "dataDateUnavailable"), alignment: result.temporal_alignment || t(lang, "alignmentUnavailable") })} />
            <WhyStep icon={<Cloud size={18} />} title={t(lang, "timelineWeatherTitle")} detail={forecast?.is_live ? t(lang, "timelineWeatherLive") : forecast?.is_sample ? forecast.expired ? t(lang, "timelineWeatherExpired") : t(lang, "timelineWeatherSample") : t(lang, "timelineWeatherUnavailable")} />
            <WhyStep icon={<CheckCircle2 size={18} />} title={t(lang, "timelineRotationTitle")} detail={tf(lang, "timelineRotationDetail", { count: options.length })} />
          </div>
        </section>

        <section className="result-section">
          <div className="result-section-heading"><h2>{t(lang, "dataDates")}</h2></div>
          <div className="comparison-wrap"><div className="dataset-table"><div className="dataset-row dataset-header"><div className="dataset-cell">{t(lang, "source")}</div><div className="dataset-cell">{t(lang, "dataDate")}</div><div className="dataset-cell">{t(lang, "resolution")}</div></div>{datasetRows.map(([name, date, resolution]) => <div className="dataset-row" key={name}><div className="dataset-cell">{name}</div><div className="dataset-cell"><span className="ltr-token">{date || "—"}</span></div><div className="dataset-cell"><span className="ltr-token">{formatResolution(resolution)}</span></div></div>)}</div></div>
        </section>

        <section className="result-section">
          <div className="result-section-heading"><h2>{t(lang, "nextSteps")}</h2></div>
          <div className="next-checklist">{bestActions.map((action) => <div key={action} className="next-check"><CheckCircle2 size={17} />{action}</div>)}</div>
        </section>

        <div className="result-actions">
          <Button asChild variant="secondary"><Link href="/analyze"><ArrowLeft size={16} className="rtl-flip" />{t(lang, "restart")}</Link></Button>
          <Button asChild><a href={`https://wa.me/?text=${encodeURIComponent(shareSummary)}`} target="_blank" rel="noreferrer"><Share2 size={16} />{t(lang, "share")}</a></Button>
          <Button asChild variant="soft"><Link href={`/expert/analysis/${encodeURIComponent(record.analysis_id)}`}>{t(lang, "expert")}<ExternalLink size={15} /></Link></Button>
        </div>
        <footer className="site-footer"><div className="footer-row"><span>{t(lang, "analysisId")}: <strong className="ltr-token">{record.analysis_id}</strong></span><span>{t(lang, "footerNote")}</span></div></footer>
      </>}
    </main>
  );
}

function formatResolution(resolution: unknown) {
  if (resolution === undefined || resolution === null || resolution === "") return "—";
  if (typeof resolution === "number") return `${resolution} m`;
  return String(resolution);
}

function Metric({ icon, label, value, sub, ltrValue }: { icon: React.ReactNode; label: string; value: string; sub: string; ltrValue?: boolean }) {
  return <article className="metric-card"><div className="flex items-center gap-2 text-green-800">{icon}<span className="metric-card-label">{label}</span></div><div className={`metric-card-value ${ltrValue ? "ltr-token" : ""}`}>{value}</div><div className="metric-card-sub">{sub}</div></article>;
}

function CompareRow({ label, values }: { label: string; values: string[] }) {
  return <tr><td>{label}</td>{values.map((value, index) => <td key={`${index}-${label}`}>{value}</td>)}</tr>;
}

function WhyStep({ icon, title, detail }: { icon: React.ReactNode; title: string; detail: string }) {
  return <article className="why-step">{icon}<h3>{title}</h3><p dir="auto">{detail}</p></article>;
}

function seasonLabel(season: string | undefined, language: Language) {
  const values: Record<Language, Record<string, string>> = {
    en: { rabi: "Rabi", kharif: "Kharif" },
    ur: { rabi: "ربیع", kharif: "خریف" },
    sd: { rabi: "ربيع", kharif: "خريف" },
  };
  if (!season) return "Season";
  const lower = season.toLowerCase();
  const base = lower.startsWith("rabi") ? values[language].rabi : lower.startsWith("kharif") ? values[language].kharif : "";
  const years = season.replace(/^(rabi|kharif)_?/i, "").replaceAll("_", "–");
  if (base) return years ? `${base} ${years}` : base;
  return season.replaceAll("_", " ");
}
