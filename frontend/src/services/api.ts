/**
 * API service layer for the Darukaa.Earth AI Biodiversity Intelligence System.
 * Wraps all FastAPI backend endpoints.
 */

export interface RetrievedEvidenceChunk {
  chunk_id: string;
  source_document: string;
  relevance_score: number;
  excerpt: string;
  key_claims: string[];
}

export interface RecommendationResponseItem {
  action: string;
  why_it_works: string;
  impacted_metrics: string[];
  time_horizon: string;
  confidence: string;
  evidence: RetrievedEvidenceChunk[];
  quantitative_estimate?: string;
  limitations: string[];
}

export interface ReasoningTraceResponse {
  input_factors: string[];
  detected_conditions: string[];
  cross_variable_relationships: string[];
  candidate_interventions: string[];
  retrieved_evidence: RetrievedEvidenceChunk[];
  validated_claims: string[];
  decision_rationale: string;
}

export interface SystemResponse {
  status: 'complete' | 'needs_clarification';
  session_id: string;
  environmental_state: Record<string, unknown>;
  clarification_required: boolean;
  missing_information?: string[];
  clarification_question?: string;
  detected_conditions?: string[];
  relationships?: Array<Record<string, unknown>>;
  recommendations?: RecommendationResponseItem[];
  reasoning_trace?: ReasoningTraceResponse;
  limitations?: string[];
}

export interface ChatRequest {
  session_id?: string;
  message: string;
}

export interface EnvironmentalState {
  // Soil Health
  soil_ph?: number;
  soil_organic_carbon_pct?: number;
  soil_moisture?: string;
  soil_condition_qualitative?: string;
  // Land Use / Land Cover
  land_use_type?: string;
  land_cover?: string;
  cropping_pattern?: string;
  // Biodiversity
  species_richness?: string;
  habitat_diversity?: string;
  biodiversity_condition?: string;
  biodiversity_indicators?: string[];
  // Climate
  temperature_celsius?: number;
  temperature_regime?: string;
  rainfall_annual_mm?: number;
  rainfall_regime?: string;
  water_availability?: string;
  // Human Impact
  pollution_pressure?: string;
  deforestation_status?: string;
  agricultural_pressure?: string;
  human_pressures?: string[];
  // Geographic
  region?: string;
}

const BASE_URL = '/api/v1';

async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail ?? `HTTP ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  health: () => fetchJSON<{ status: string }>(`${BASE_URL}/health`),

  chat: (request: ChatRequest): Promise<SystemResponse> =>
    fetchJSON(`${BASE_URL}/chat`, { method: 'POST', body: JSON.stringify(request) }),

  assessment: (state: EnvironmentalState, sessionId?: string): Promise<SystemResponse> => {
    const url = sessionId
      ? `${BASE_URL}/assessment?session_id=${encodeURIComponent(sessionId)}`
      : `${BASE_URL}/assessment`;
    return fetchJSON(url, { method: 'POST', body: JSON.stringify(state) });
  },

  getSession: (sessionId: string) =>
    fetchJSON<Record<string, unknown>>(`${BASE_URL}/session/${sessionId}`),
};
