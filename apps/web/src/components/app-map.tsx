"use client";

import { useEffect, useRef, useState } from "react";
import { Layers2, LocateFixed, MapPin } from "lucide-react";
import type { Map as MapLibreMap, Marker } from "maplibre-gl";
import { api } from "@/lib/api";
import type { LayerCatalog, LayerInfo } from "@/lib/types";

type Point = { lat: number; lon: number };
type Props = {
  mode?: "picker" | "layers";
  selectedPoint?: Point | null;
  onPointSelect?: (point: Point) => void;
  className?: string;
  ariaLabel?: string;
  layerOpacity?: number;
  showAnalysisRadius?: boolean;
  labels?: { base: string; ndvi: string; ndmi: string; bsi: string; slope: string; layers: string };
};

const layerNames: Record<string, string> = { ndvi: "Vegetation", ndmi: "Moisture", bsi: "Bare soil", slope: "Slope" };
const layerGradients: Record<string, string> = {
  ndvi: "linear-gradient(90deg, #92400e 0%, #eab308 45%, #15803d 100%)",
  ndmi: "linear-gradient(90deg, #d97706 0%, #e0f2fe 50%, #0369a1 100%)",
  bsi: "linear-gradient(90deg, #15803d 0%, #fde68a 50%, #9a3412 100%)",
  slope: "linear-gradient(90deg, #16a34a 0%, #facc15 55%, #b91c1c 100%)",
};

function analysisRadiusFeature(point: Point, radiusMeters = 150) {
  const earthRadiusMeters = 6_371_008.8;
  const angularDistance = radiusMeters / earthRadiusMeters;
  const lat1 = point.lat * Math.PI / 180;
  const lon1 = point.lon * Math.PI / 180;
  const ring: [number, number][] = [];
  for (let index = 0; index <= 64; index += 1) {
    const bearing = index / 64 * Math.PI * 2;
    const lat2 = Math.asin(Math.sin(lat1) * Math.cos(angularDistance) + Math.cos(lat1) * Math.sin(angularDistance) * Math.cos(bearing));
    const lon2 = lon1 + Math.atan2(
      Math.sin(bearing) * Math.sin(angularDistance) * Math.cos(lat1),
      Math.cos(angularDistance) - Math.sin(lat1) * Math.sin(lat2),
    );
    ring.push([lon2 * 180 / Math.PI, lat2 * 180 / Math.PI]);
  }
  return { type: "Feature" as const, properties: { radius_m: radiusMeters }, geometry: { type: "Polygon" as const, coordinates: [ring] } };
}

export function AppMap({ mode = "picker", selectedPoint, onPointSelect, className, ariaLabel = "Interactive field map", layerOpacity = 0.78, showAnalysisRadius = false, labels }: Props) {
  const element = useRef<HTMLDivElement>(null);
  const map = useRef<MapLibreMap | null>(null);
  const marker = useRef<Marker | null>(null);
  const catalog = useRef<LayerCatalog | null>(null);
  const activeLayer = useRef("base");
  const [layer, setLayer] = useState("base");
  const [layerInfo, setLayerInfo] = useState<LayerInfo | null>(null);
  const [mapReady, setMapReady] = useState(false);
  const [catalogReady, setCatalogReady] = useState(false);
  const [layerUnavailable, setLayerUnavailable] = useState(false);

  useEffect(() => {
    let alive = true;
    let clickHandler: ((event: { lngLat: { lat: number; lng: number } }) => void) | undefined;
    (async () => {
      if (!element.current) return;
      try {
        const module = await import("maplibre-gl");
        if (!alive || !element.current) return;
        module.setWorkerUrl?.("/maplibre-gl-worker.mjs");
        const Map = module.Map;
        const center: [number, number] = selectedPoint ? [selectedPoint.lon, selectedPoint.lat] : [68.37, 25.39];
        const instance = new Map({
          container: element.current,
          center,
          zoom: selectedPoint ? 12.5 : 9.5,
          attributionControl: false,
          style: {
            version: 8,
            sources: { osm: { type: "raster", tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"], tileSize: 256, attribution: "© OpenStreetMap contributors" } },
            layers: [{ id: "osm", type: "raster", source: "osm", paint: { "raster-saturation": -0.25, "raster-contrast": -0.05 } }],
          },
        });
        const { NavigationControl, AttributionControl, Marker } = module;
        instance.addControl(new NavigationControl({ showCompass: false }), "top-right");
        instance.addControl(new AttributionControl({ compact: true }), "bottom-right");
        map.current = instance;
        if (selectedPoint) marker.current = new Marker({ color: "#166534" }).setLngLat([selectedPoint.lon, selectedPoint.lat]).addTo(instance);
        if (mode === "picker") {
          clickHandler = (event) => {
            const point = { lat: event.lngLat.lat, lon: event.lngLat.lng };
            marker.current?.remove();
            marker.current = new Marker({ color: "#166534" }).setLngLat([point.lon, point.lat]).addTo(instance);
            onPointSelect?.(point);
          };
          instance.on("click", clickHandler);
        } else {
          try { catalog.current = await api.layers(); setCatalogReady(true); }
          catch { setLayerUnavailable(true); }
        }
        instance.on("load", () => { if (alive) setMapReady(true); });
      } catch {
        if (alive) setLayerUnavailable(true);
      }
    })();
    return () => {
      alive = false;
      if (clickHandler) map.current?.off("click", clickHandler);
      marker.current?.remove();
      map.current?.remove();
      map.current = null;
      marker.current = null;
    };
    // The map instance is created once; changing coordinates is handled separately.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mode]);

  useEffect(() => {
    if (!map.current || !selectedPoint) return;
    map.current.flyTo({ center: [selectedPoint.lon, selectedPoint.lat], zoom: Math.max(map.current.getZoom(), 12.5) });
    if (mode === "picker") {
      marker.current?.remove();
      import("maplibre-gl").then(({ Marker }) => {
        if (map.current) marker.current = new Marker({ color: "#166534" }).setLngLat([selectedPoint.lon, selectedPoint.lat]).addTo(map.current);
      });
    }
  }, [selectedPoint, mode]);

  useEffect(() => {
    const instance = map.current;
    if (!instance || mode !== "layers" || !mapReady || !catalog.current) return;
    const previous = activeLayer.current;
    if (previous !== "base") {
      if (instance.getLayer("agrishift-layer")) instance.removeLayer("agrishift-layer");
      if (instance.getSource("agrishift-layer")) instance.removeSource("agrishift-layer");
    }
    activeLayer.current = layer;
    if (layer === "base") {
      setLayerInfo(null);
      return;
    }
    const info = catalog.current.layers[layer];
    const bounds = info?.bounds || catalog.current.bounds;
    if (!info || !bounds) { setLayerInfo(null); setLayerUnavailable(true); return; }
    setLayerInfo(info);
    const coordinates: [[number, number], [number, number], [number, number], [number, number]] = [
      [bounds.west, bounds.north], [bounds.east, bounds.north], [bounds.east, bounds.south], [bounds.west, bounds.south],
    ];
    instance.addSource("agrishift-layer", {
      type: "image",
      url: `${process.env.NEXT_PUBLIC_AGRISHIFT_API_URL || "http://127.0.0.1:8000"}/api/v1/layers/${layer}.png`,
      coordinates,
    });
    instance.addLayer({ id: "agrishift-layer", type: "raster", source: "agrishift-layer", paint: { "raster-opacity": Math.max(0, Math.min(1, layerOpacity)) } });
    if (instance.getLayer("analysis-radius-fill")) instance.moveLayer("analysis-radius-fill");
    if (instance.getLayer("analysis-radius-outline")) instance.moveLayer("analysis-radius-outline");
    setLayerUnavailable(false);
  }, [layer, mapReady, catalogReady, mode]);

  useEffect(() => {
    const instance = map.current;
    if (!instance?.getLayer("agrishift-layer")) return;
    instance.setPaintProperty("agrishift-layer", "raster-opacity", Math.max(0, Math.min(1, layerOpacity)));
  }, [layerOpacity, layer, mapReady]);

  useEffect(() => {
    const instance = map.current;
    if (!instance || mode !== "layers" || !showAnalysisRadius || !mapReady || !selectedPoint) return;
    if (instance.getLayer("analysis-radius-outline")) instance.removeLayer("analysis-radius-outline");
    if (instance.getLayer("analysis-radius-fill")) instance.removeLayer("analysis-radius-fill");
    if (instance.getSource("analysis-radius")) instance.removeSource("analysis-radius");
    instance.addSource("analysis-radius", { type: "geojson", data: analysisRadiusFeature(selectedPoint) });
    instance.addLayer({
      id: "analysis-radius-fill", type: "fill", source: "analysis-radius",
      paint: { "fill-color": "#22c55e", "fill-opacity": 0.13 },
    });
    instance.addLayer({
      id: "analysis-radius-outline", type: "line", source: "analysis-radius",
      paint: { "line-color": "#14532d", "line-width": 2, "line-dasharray": [2, 2] },
    });
  }, [showAnalysisRadius, selectedPoint?.lat, selectedPoint?.lon, mapReady, mode]);

  const chooseLayer = (name: string) => setLayer(name);
  const activeLabel = layer === "base" ? "" : (labels?.[layer as "ndvi" | "ndmi" | "bsi" | "slope"] || layerNames[layer] || layer.toUpperCase());

  return (
    <div className={`map-shell ${className || ""}`} aria-label={ariaLabel}>
      <div ref={element} className="map-canvas" role="application" aria-label={ariaLabel} />
      {mode === "picker" && <div className="map-hint"><MapPin size={16} /> Tap the map to set your field</div>}
      {mode === "layers" && (
        <div className="map-layer-control" role="group" aria-label="Map layers">
          <span className="map-control-label"><Layers2 size={15} />{labels?.layers || "Layers"}</span>
          {(["base", "ndvi", "ndmi", "bsi", "slope"] as const).map((name) => (
            <button key={name} type="button" className={layer === name ? "map-layer active" : "map-layer"} onClick={() => chooseLayer(name)} aria-pressed={layer === name}>
              {name === "base" ? labels?.base || "Base" : labels?.[name as "ndvi" | "ndmi" | "bsi" | "slope"] || layerNames[name]}
            </button>
          ))}
        </div>
      )}
      {mode === "layers" && layer !== "base" && layerInfo && (
        <div className="map-legend" role="region" aria-label={`${activeLabel} layer legend`}>
          <div className="map-legend-top">
            <strong>{activeLabel} ({layer.toUpperCase()})</strong>
            <span>{layerInfo.observation_date || "—"} · {layerInfo.source_resolution_m ? `${layerInfo.source_resolution_m} m` : "—"}</span>
          </div>
          <div className="map-legend-bar" style={{ background: layerGradients[layer] || layerGradients.ndvi }} />
          <div className="map-legend-scale">
            <span>{typeof layerInfo.minimum === "number" ? layerInfo.minimum.toFixed(2) : "—"}</span>
            <span>{layerInfo.unit || ""}</span>
            <span>{typeof layerInfo.maximum === "number" ? layerInfo.maximum.toFixed(2) : "—"}</span>
          </div>
        </div>
      )}
      {mode === "picker" && (
        <button className="map-locate" type="button" aria-label="Use current location" onClick={() => navigator.geolocation?.getCurrentPosition((position) => onPointSelect?.({ lat: position.coords.latitude, lon: position.coords.longitude }), () => setLayerUnavailable(true))}>
          <LocateFixed size={17} />
        </button>
      )}
      {layerUnavailable && <div className="map-error">{mode === "layers" ? "Layer metadata or map tiles unavailable." : "Location could not be read. Tap the map to place a pin."}</div>}
    </div>
  );
}
