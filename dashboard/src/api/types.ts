// TypeScript mirror of dashboard_api/schemas.py — the API contract.

export interface Stat {
  label: string;
  value: string;
  delta: string | null;
  tone: 'positive' | 'neutral';
}

export interface Readiness {
  name: string;
  status: string;
}

export interface BackendPanel {
  serving: string;
  model: string;
  quant: string;
  readiness: Readiness[];
  note: string | null;
}

export interface OverviewPayload {
  stats: Stat[];
  requests_series: number[];
  backend: BackendPanel;
}

export interface RegistryModel {
  name: string;
  version: string;
  quantization: string;
  tasks: string[];
  backend: string;
  status: 'active' | 'candidate';
}

export interface Route {
  task: string;
  model: string;
  backend: string;
}

export interface RegistryPayload {
  models: RegistryModel[];
  routing: Route[];
}

export interface LeaderboardRow {
  name: string;
  scores: Record<string, number>;
  overall: number;
  curated: boolean;
}

export interface LeaderboardPayload {
  tasks: string[];
  rows: LeaderboardRow[];
  note: string | null;
}

export interface SurfaceShare {
  label: string;
  pct: number;
  color: 'indigo' | 'emerald' | 'sky';
}

export interface AdoptionPayload {
  stats: Stat[];
  usage_series: number[];
  by_surface: SurfaceShare[];
}

export interface ContextSource {
  name: string;
  path: string;
  docs_label: string;
  chunks: number;
  icon: 'code' | 'book' | 'alert' | 'layers';
  color: 'indigo' | 'emerald' | 'amber' | 'violet';
}

export interface RetrievalHit {
  title: string;
  path: string;
  snippet: string;
  score: number;
}

export interface ContextPayload {
  total_chunks: number;
  updated: string;
  sources: ContextSource[];
  query: string;
  results: RetrievalHit[];
}
