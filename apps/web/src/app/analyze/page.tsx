"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, ArrowRight, Check, CircleHelp, Droplets, LocateFixed, MapPin, Sprout, Wheat } from "lucide-react";
import { AppMap } from "@/components/app-map";
import { Brand } from "@/components/brand";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { api, rememberAnalysis } from "@/lib/api";
import { direction, t } from "@/lib/i18n";
import type { AnalyzePayload, Crop, Language } from "@/lib/types";

const places = [
  { name: "Hyderabad", lat: 25.396, lon: 68.357 },
  { name: "Qasimabad", lat: 25.407, lon: 68.311 },
  { name: "Latifabad", lat: 25.369, lon: 68.341 },
  { name: "Tando Jam", lat: 25.428, lon: 68.529 },
  { name: "Jamshoro", lat: 25.430, lon: 68.281 },
  { name: "Matiari", lat: 25.598, lon: 68.447 },
  { name: "Hala", lat: 25.814, lon: 68.422 },
];

const cropIcon = (id: string) => /wheat|mustard|millet|sorghum/.test(id) ? Wheat : Sprout;

export default function AnalyzePage() {
  const router = useRouter();
  const [language, setLanguage] = useState<Language>("en");
  const [step, setStep] = useState(1);
  const [point, setPoint] = useState<{ lat: number; lon: number } | null>(null);
  const [placeName, setPlaceName] = useState("");
  const [query, setQuery] = useState("");
  const [currentCrop, setCurrentCrop] = useState("");
  const [previousCrop, setPreviousCrop] = useState("");
  const [crops, setCrops] = useState<Crop[]>([]);
  const [cropsLoading, setCropsLoading] = useState(true);
  const [waterSource, setWaterSource] = useState<AnalyzePayload["water_source"] | "">("");
  const [waterAmount, setWaterAmount] = useState<AnalyzePayload["water_amount"] | "">("");
  const [salinity, setSalinity] = useState<AnalyzePayload["salinity"]>("unknown");
  const [waterlogging, setWaterlogging] = useState<AnalyzePayload["waterlogging"]>("unknown");
  const [priority, setPriority] = useState<AnalyzePayload["priority"]>("balanced");
  const [error, setError] = useState("");
  const [processing, setProcessing] = useState(false);
  const [processingStage, setProcessingStage] = useState(0);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const requested = params.get("lang");
    const saved = window.localStorage.getItem("agrishift:language");
    const lang = (requested === "ur" || requested === "sd" || requested === "en" ? requested : saved === "ur" || saved === "sd" || saved === "en" ? saved : "en") as Language;
    setLanguage(lang);
    document.documentElement.lang = lang;
    document.documentElement.dir = direction(lang);
    api.crops().then(setCrops).catch((reason: Error) => setError(reason.message)).finally(() => setCropsLoading(false));
  }, []);

  useEffect(() => {
    document.documentElement.lang = language;
    document.documentElement.dir = direction(language);
    window.localStorage.setItem("agrishift:language", language);
  }, [language]);

  useEffect(() => {
    if (!processing) return;
    const timer = window.setInterval(() => setProcessingStage((current) => (current + 1) % 4), 1200);
    return () => window.clearInterval(timer);
  }, [processing]);

  const filteredPlaces = useMemo(() => places.filter((place) => place.name.toLowerCase().includes(query.toLowerCase())), [query]);
  const cropById = useMemo(() => new Map(crops.map((crop) => [crop.id, crop])), [crops]);
  const labelCrop = (id: string) => cropById.get(id)?.names[language] || id;
  const changeLanguage = (value: Language) => setLanguage(value);
  const setPlace = (name: string, lat: number, lon: number) => {
    setPoint({ lat, lon });
    setPlaceName(name);
    setQuery(name);
    setError("");
  };
  const useCurrentLocation = () => {
    setError("");
    if (!navigator.geolocation) { setError(t(language, "locateFailed")); return; }
    navigator.geolocation.getCurrentPosition(
      ({ coords }) => { setPoint({ lat: coords.latitude, lon: coords.longitude }); setPlaceName("Current location"); },
      () => setError(t(language, "locateFailed")),
      { enableHighAccuracy: true, timeout: 12000 },
    );
  };

  const continueStep = () => {
    setError("");
    if (step === 1 && !point) { setError(t(language, "locationRequired")); return; }
    if (step === 2 && !currentCrop) { setError(t(language, "cropRequired")); return; }
    if (step === 3 && (!waterSource || !waterAmount)) { setError(t(language, "waterSource") + " · " + t(language, "waterAmount")); return; }
    setStep((value) => Math.min(5, value + 1));
  };

  const submit = async () => {
    if (!point || !currentCrop || !waterSource || !waterAmount) return;
    setError("");
    setProcessing(true);
    setProcessingStage(0);
    const payload: AnalyzePayload = {
      lat: point.lat, lon: point.lon, radius_m: 150, current_crop: currentCrop,
      previous_crop: previousCrop || "unknown", water_source: waterSource,
      water_amount: waterAmount, salinity, waterlogging, priority, language,
    };
    try {
      const result = await api.analyze(payload);
      const id = result.analysis_id;
      if (!id) throw new Error("The API did not return an analysis ID.");
      rememberAnalysis(id);
      router.push(`/results/${encodeURIComponent(id)}`);
    } catch (reason) {
      setProcessing(false);
      setError(reason instanceof Error ? reason.message : t(language, "unavailable"));
    }
  };

  const Question = ({ children }: { children: React.ReactNode }) => <h2 className="wizard-panel-title">{children}</h2>;
  const Choice = ({ value, selected, label, onClick }: { value: string; selected: boolean; label: string; onClick: (value: string) => void }) => (
    <button type="button" className={selected ? "choice selected" : "choice"} aria-pressed={selected} onClick={() => onClick(value)}>
      <span className="choice-dot">{selected && <Check size={12} />}</span><span>{label}</span>
    </button>
  );

  return (
    <main className="farmer-page" lang={language} dir={direction(language)}>
      <header className="farmer-header">
        <div className="frame farmer-header-inner">
          <Brand />
          <div className="flex items-center gap-1 rounded-xl border border-slate-200 bg-white p-1" aria-label="Language">
            {(["en", "ur", "sd"] as Language[]).map((lang) => <button key={lang} type="button" onClick={() => changeLanguage(lang)} aria-pressed={language === lang} className={`min-h-11 min-w-11 rounded-lg px-2 text-xs font-bold ${language === lang ? "bg-green-50 text-green-900" : "text-slate-600"}`}>{lang === "en" ? "EN" : lang === "ur" ? "اردو" : "سنڌي"}</button>)}
          </div>
        </div>
      </header>
      <div className="frame wizard-layout">
        <section className="wizard-main" aria-live="polite">
          <div className="flex items-center justify-between gap-3">
            <div><p className="section-kicker">{t(language, "step")} {step} {t(language, "of")} 5</p><h1 className="wizard-heading">{step === 1 ? t(language, "location") : step === 2 ? t(language, "crops") : step === 3 ? t(language, "soilWater") : step === 4 ? t(language, "priority") : t(language, "review")}</h1></div>
            <Badge tone="green">Hyderabad pilot</Badge>
          </div>
          <div className="progress-steps" aria-label={`Step ${step} of 5`}>
            {([1, 2, 3, 4, 5] as const).map((number) => <div key={number} className={`progress-step ${step === number ? "active" : step > number ? "done" : ""}`}><span className="progress-number">{step > number ? <Check size={14} /> : number}</span><span className="progress-step-label">{number === 1 ? t(language, "location") : number === 2 ? t(language, "crops") : number === 3 ? t(language, "soilWater") : number === 4 ? t(language, "priority") : t(language, "review")}</span></div>)}
          </div>

          {processing ? (
            <div className="wizard-panel text-center" role="status">
              <div className="spinner mx-auto mt-5" />
              <h2 className="mt-4 text-xl font-semibold">{t(language, "processing")}</h2>
              <div className="processing-list text-left">
                {(["stage1", "stage2", "stage3", "stage4"] as const).map((key, index) => <div className={`processing-stage ${processingStage === index ? "active" : ""}`} key={key}>{processingStage === index ? <span className="spinner" /> : <Check size={18} />}<span>{t(language, key)}</span></div>)}
              </div>
            </div>
          ) : (
            <div className="wizard-panel">
              {step === 1 && <>
                <Question>{t(language, "location")}</Question><p className="wizard-panel-copy">{t(language, "locationHelp")}</p>
                <div className="search-row">
                  <div className="flex min-w-0 flex-1 gap-2">
                    <Input aria-label={t(language, "searchTown")} placeholder={t(language, "searchTown")} value={query} onChange={(event) => setQuery(event.target.value)} list="towns" />
                    <datalist id="towns">{places.map((place) => <option key={place.name} value={place.name} />)}</datalist>
                    <Button type="button" variant="secondary" onClick={() => { const place = places.find((item) => item.name.toLowerCase() === query.toLowerCase()); if (place) setPlace(place.name, place.lat, place.lon); }}>{t(language, "find")}</Button>
                  </div>
                  <Button type="button" variant="soft" onClick={useCurrentLocation}><LocateFixed size={16} />{t(language, "useLocation")}</Button>
                </div>
                {query && filteredPlaces.length > 0 && query.toLowerCase() !== placeName.toLowerCase() && <div className="place-suggestions" role="listbox">{filteredPlaces.slice(0, 4).map((place) => <button key={place.name} type="button" role="option" aria-selected={place.name === placeName} onClick={() => setPlace(place.name, place.lat, place.lon)}><MapPin size={15} />{place.name}<span>Sindh</span></button>)}</div>}
                <AppMap mode="picker" selectedPoint={point} onPointSelect={(value) => { setPoint(value); setPlaceName("Pinned field"); setError(""); }} ariaLabel={t(language, "placePin")} />
                {point && <div className="selected-location"><span className="flex items-center gap-2"><MapPin size={16} color="#166534" />{t(language, "selected")}</span><strong>{placeName || "Pinned field"}</strong></div>}
              </>}

              {step === 2 && <>
                <Question>{t(language, "crops")}</Question><p className="wizard-panel-copy">Choose the crops you remember. Previous crop is optional.</p>
                <label className="field-label">{t(language, "currentCrop")}</label>
                {cropsLoading ? <div className="py-8 text-sm text-slate-500">Loading crop list…</div> : crops.length === 0 ? <div className="error-text">Crop list unavailable from the analysis API. {error}</div> : <div className="crop-pick-grid" role="group" aria-label={t(language, "currentCrop")}>{crops.map((crop) => { const Icon = cropIcon(crop.id); return <button type="button" key={crop.id} className={`crop-pick ${currentCrop === crop.id ? "selected" : ""}`} aria-pressed={currentCrop === crop.id} onClick={() => setCurrentCrop(crop.id)}><Icon size={20} /><span>{crop.names[language] || crop.names.en}</span></button>; })}</div>}
                <div className="mt-6"><label className="field-label" htmlFor="previous-crop">{t(language, "previousCrop")}</label><select id="previous-crop" value={previousCrop} onChange={(event) => setPreviousCrop(event.target.value)} className="h-11 w-full rounded-xl border border-slate-300 bg-white px-3.5 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-green-700"><option value="">{t(language, "unknown")}</option>{crops.filter((crop) => crop.id !== currentCrop).map((crop) => <option key={crop.id} value={crop.id}>{crop.names[language] || crop.names.en}</option>)}</select></div>
              </>}

              {step === 3 && <>
                <Question>{t(language, "soilWater")}</Question><p className="wizard-panel-copy">Choose the closest answer; you can leave uncertain soil signs as “not sure”.</p>
                <div className="form-stack">
                  <div><label className="field-label">{t(language, "waterSource")}</label><div className="choice-row">{(["canal", "tubewell", "rain"] as const).map((value) => <Choice key={value} value={value} selected={waterSource === value} label={t(language, value)} onClick={(v) => setWaterSource(v as typeof waterSource)} />)}</div></div>
                  <div><label className="field-label">{t(language, "waterAmount")}</label><div className="choice-row">{(["low", "medium", "high"] as const).map((value) => <Choice key={value} value={value} selected={waterAmount === value} label={t(language, value)} onClick={(v) => setWaterAmount(v as typeof waterAmount)} />)}</div></div>
                  <div><label className="field-label">{t(language, "salinity")}</label><div className="choice-row">{(["yes", "no", "unknown"] as const).map((value) => <Choice key={value} value={value} selected={salinity === value} label={t(language, value)} onClick={(v) => setSalinity(v as typeof salinity)} />)}</div></div>
                  <div><label className="field-label">{t(language, "waterlogging")}</label><div className="choice-row">{(["yes", "no", "unknown"] as const).map((value) => <Choice key={value} value={value} selected={waterlogging === value} label={t(language, value)} onClick={(v) => setWaterlogging(v as typeof waterlogging)} />)}</div></div>
                </div>
              </>}

              {step === 4 && <>
                <Question>{t(language, "priority")}</Question><p className="wizard-panel-copy">{t(language, "priorityHelp")}</p>
                <div className="priority-grid">{(["save_water", "improve_soil", "balanced"] as const).map((value) => { const Icon = value === "save_water" ? Droplets : value === "improve_soil" ? Sprout : CircleHelp; return <button type="button" key={value} className={`priority-choice ${priority === value ? "selected" : ""}`} aria-pressed={priority === value} onClick={() => setPriority(value)}><Icon size={24} /><strong>{t(language, value)}</strong><span className="text-xs text-slate-500">{value === "save_water" ? "Water availability matters most" : value === "improve_soil" ? "Soil recovery matters most" : "Compare across several needs"}</span></button>; })}</div>
              </>}

              {step === 5 && <>
                <Question>{t(language, "review")}</Question><p className="wizard-panel-copy">Your answers are sent to the AgriShift analysis API. No result is guessed if required data is missing.</p>
                <div className="review-list">
                  <div className="review-item"><span>{t(language, "locationLabel")}</span><strong>{placeName || "Pinned field"}</strong></div>
                  <div className="review-item"><span>{t(language, "currentCrop")}</span><strong>{labelCrop(currentCrop)}</strong></div>
                  <div className="review-item"><span>{t(language, "previousCrop")}</span><strong>{previousCrop ? labelCrop(previousCrop) : t(language, "unknown")}</strong></div>
                  <div className="review-item"><span>{t(language, "waterSource")} · {t(language, "waterAmount")}</span><strong>{waterSource ? t(language, waterSource) : "—"} · {waterAmount ? t(language, waterAmount) : "—"}</strong></div>
                  <div className="review-item"><span>{t(language, "salinity")}</span><strong>{t(language, salinity)}</strong></div>
                  <div className="review-item"><span>{t(language, "waterlogging")}</span><strong>{t(language, waterlogging)}</strong></div>
                  <div className="review-item"><span>{t(language, "priorityLabel")}</span><strong>{t(language, priority)}</strong></div>
                </div>
              </>}

              {error && <p className="error-text mt-5" role="alert">{error}</p>}
              <div className="wizard-footer">
                <Button variant="secondary" type="button" disabled={step === 1} onClick={() => { setError(""); setStep((value) => Math.max(1, value - 1)); }}><ArrowLeft size={16} className="rtl-flip" />{t(language, "back")}</Button>
                {step < 5 ? <Button type="button" onClick={continueStep}>{t(language, "next")} <ArrowRight size={16} className="rtl-flip" /></Button> : <Button type="button" onClick={submit}><MapPin size={16} />{t(language, "analyzeButton")}</Button>}
              </div>
            </div>
          )}
        </section>
        <aside className="wizard-aside"><h3>{t(language, "callout")}</h3><p>AgriShift uses the nearest validated environmental point. A result may be unavailable beyond the pilot coverage or when core data is missing.</p><Link className="mt-3 inline-flex min-h-11 items-center gap-1 text-sm font-semibold text-green-800 underline underline-offset-4" href="/">About this pilot <ArrowRight size={14} className="rtl-flip" /></Link></aside>
      </div>
      <footer className="frame mt-8 flex flex-wrap items-center justify-between gap-3 border-t border-slate-200 pt-4 text-xs text-slate-500"><span>AgriShift AI · Hyderabad pilot</span><span>Satellite signals support local expert review.</span></footer>
    </main>
  );
}
