export type {
  SystemResponse,
  RecommendationResponseItem,
  ReasoningTraceResponse,
  RetrievedEvidenceChunk,
  ChatRequest,
  EnvironmentalState,
} from '../services/api';

import type { SystemResponse } from '../services/api';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  response?: SystemResponse;
}

export type TabId = 'chat' | 'structured' | 'trace';

export const DEMO_SCENARIOS = [
  {
    id: 'degraded-wheat',
    label: 'Degraded Wheat Farm',
    description: 'Acidic soil, pesticide overuse, low biodiversity',
    icon: '🌾',
    state: {
      soil_ph: 4.8,
      soil_organic_carbon_pct: 0.6,
      soil_moisture: 'dry',
      land_use_type: 'cropland',
      land_cover: 'wheat monoculture',
      cropping_pattern: 'monoculture',
      species_richness: 'low',
      habitat_diversity: 'low',
      biodiversity_condition: 'degraded',
      temperature_celsius: 34,
      rainfall_annual_mm: 480,
      rainfall_regime: 'low',
      water_availability: 'drought_prone',
      pollution_pressure: 'synthetic_chemicals_and_fertilizers',
      agricultural_pressure: 'intensive_tillage',
      human_pressures: ['chemical_pollution', 'monoculture_stress'],
    },
  },
  {
    id: 'forest-edge',
    label: 'Forest-Edge Farm',
    description: 'Healthy soil, mixed crops, deforestation pressure nearby',
    icon: '🌿',
    state: {
      soil_ph: 6.5,
      soil_organic_carbon_pct: 2.8,
      soil_moisture: 'adequate',
      land_use_type: 'agroforestry',
      land_cover: 'mixed vegetation',
      cropping_pattern: 'crop_rotation',
      species_richness: 'moderate',
      habitat_diversity: 'high',
      biodiversity_condition: 'moderate',
      temperature_celsius: 26,
      rainfall_annual_mm: 1200,
      rainfall_regime: 'high',
      water_availability: 'adequate',
      pollution_pressure: 'low',
      deforestation_status: 'nearby_deforestation',
      human_pressures: ['deforestation'],
    },
  },
  {
    id: 'dry-degraded',
    label: 'Arid Degraded Land',
    description: 'Drought-prone, deforested, severe soil erosion',
    icon: '🏜️',
    state: {
      soil_ph: 8.1,
      soil_organic_carbon_pct: 0.3,
      soil_moisture: 'severely_depleted',
      soil_condition_qualitative: 'degraded',
      land_use_type: 'degraded land',
      land_cover: 'sparse_cover',
      cropping_pattern: 'monoculture',
      species_richness: 'very low',
      habitat_diversity: 'very low',
      biodiversity_condition: 'critically degraded',
      temperature_celsius: 38,
      rainfall_annual_mm: 250,
      rainfall_regime: 'arid',
      water_availability: 'scarce',
      pollution_pressure: 'synthetic_fertilizer_overuse',
      deforestation_status: 'recent_deforestation',
      agricultural_pressure: 'intensive_tillage',
      human_pressures: ['deforestation', 'chemical_pollution', 'overgrazing'],
    },
  },
] as const;

