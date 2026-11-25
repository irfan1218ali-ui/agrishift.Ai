export type Language = "en" | "ur" | "sd";

export interface AnalyzePayload {
  lat: number;
  lon: number;
  radius_m: number;
  current_crop: string;
  previous_crop: string;
  water_source: "canal" | "tubewell" | "rain";
  water_amount: "low" | "medium" | "high";
  salinity: "yes" | "no" | "unknown";
  waterlogging: "yes" | "no" | "unknown";
  priority: "save_water" | "improve_soil" | "balanced";
  language: Language;
}

export interface Crop {
  id: string;
  season?: string | null;
  names: Record<Language, string>;
  picture_url?: string | null;
  verified?: boolean;
  special?: string;
}

export interface RotationOption {
  id: string;
  seasons: { season: string; crop: string }[];
  light: "green" | "yellow" | "red";
  water_drops: number;
  score: number;
  confidence_score?: number;
  confidence_dots: number;
  why_ids?: string[];
  caution_ids?: string[];
  expert_needed?: boolean;
  crop_verified?: boolean;
  warnings?: string[];
  warning_ids?: string[];
}

export interface WeatherDay {
  date: string;
  tmax_c?: number;
  tmin_c?: number;
  rain_total_mm?: number;
  rh_mean?: number;
  wind_max_ms?: number;
}

export interface Forecast {
  available: boolean;
  status: "live" | "sample" | "expired" | "unavailable" | string;
  is_live?: boolean;
  is_sample?: boolean;
  expired?: boolean;
  generated_at?: string;
  valid_from?: string;
  valid_until?: string;
  days?: WeatherDay[];
}

export interface AnalysisResult {
  status: "ok" | "not_applicable" | "insufficient_data" | string;
  reason_id?: string;
  analysis_id?: string;
  is_demo?: boolean;
  data_mode?: "REAL" | "DEMO" | string;
  analysis_method?: string;
  data_snapshot?: {
    landsat_date?: string;
    source_dates?: Record<string, string>;
    source_resolutions?: Record<string, number | string>;
  };
  feature_point_id?: string;
  feature_point?: {
    id?: string;
    distance_m?: number;
    analysis_radius_m?: number;
    grid_spacing_m?: number;
  };
  field_context?: {
    vegetation_condition?: { light?: string; template_id?: string };
    cluster?: { cluster_id?: number; cluster_label?: string; interpretation?: string };
    cluster_label?: string;
    cluster_id?: number;
    environmental_features?: Record<string, unknown>;
  };
  weather?: Forecast;
  forecast?: Forecast;
  options?: RotationOption[];
  rotation_options?: RotationOption[];
  confidence?: { score?: number; dots?: string; reasons?: string[]; formula?: Record<string, number> };
  dataset_metadata?: Record<string, { observation_date?: string; period?: string; resolution?: number | string; scene?: string }>;
  model_metadata?: { name?: string | null; version?: string | null; status?: string };
  temporal_alignment?: string;
  regional_context_status?: string;
  limitations?: string[];
}

export interface StoredAnalysis {
  analysis_id: string;
  request: {
    latitude: number;
    longitude: number;
    previous_crop?: string | null;
    current_crop: string;
    water_source: string;
    water_level: string;
    salinity: string;
    waterlogging: string;
    priority: string;
    language: Language;
    created_at?: string;
  };
  result: AnalysisResult;
  review_status?: "not_reviewed" | "under_review" | "approved" | "approved_with_changes" | "needs_more_information" | "unsuitable";
}

export interface ScoreComponent {
  value: number;
  reason: string;
  rule_id: string;
  verified: boolean;
  source: string;
}

export interface ExpertReview {
  review_id: string;
  analysis_id: string;
  expert_user_id: string;
  decision: "approved" | "approved_with_changes" | "needs_more_information" | "unsuitable" | null;
  comments: string;
  suggested_rotation: Array<Record<string, unknown>> | Record<string, unknown> | null;
  soil_test_requested: boolean;
  reviewed_at: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface ExpertNote {
  analysis_id: string;
  content: string;
  created_at: string | null;
  updated_at: string | null;
}

export interface ExpertAnalysisDetail {
  analysis: StoredAnalysis;
  review_status: NonNullable<StoredAnalysis["review_status"]>;
  score_breakdown: Record<string, Record<string, ScoreComponent>>;
  reviews: ExpertReview[];
  notes: ExpertNote;
}

export interface ExpertAnalysisList {
  items: StoredAnalysis[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ExpertSummary {
  total_analyses: number;
  pending_reviews: number;
  low_confidence_analyses: number;
  completed_reviews: number;
  recent_analyses: StoredAnalysis[];
}

export interface Health {
  status: string;
  features_available: boolean;
  demo_mode: boolean;
  data_mode: string;
  environmental_clustering: string;
  crops?: number;
}

export interface LayerInfo {
  file: string;
  provider: string;
  product: string;
  observation_date: string;
  source_resolution_m: number;
  unit: string;
  minimum?: number;
  maximum?: number;
  color_scale?: string;
  limitation: string;
  bounds?: { west: number; south: number; east: number; north: number };
}

export interface LayerCatalog {
  bounds: { west: number; south: number; east: number; north: number };
  layers: Record<string, LayerInfo>;
}
