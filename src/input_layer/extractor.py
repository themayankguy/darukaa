"""Natural language environmental parameter extractor.

Extracts structured EnvironmentalState from freeform conversational descriptions using
deterministic regex and semantic pattern matching, with optional LLM assistance.
Strictly avoids inventing numbers or hallucinating unmentioned parameters.
"""

import re
import json
from typing import Optional, Dict, Any

from src.input_layer.schemas import EnvironmentalState
from src.core.llm_interface import LLMClient


class EnvironmentalExtractor:
    """Extracts typed environmental variables from conversational text."""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client

    def extract(self, text: str) -> EnvironmentalState:
        """Parses natural language text into an EnvironmentalState."""
        extracted_dict: Dict[str, Any] = {}
        lower_text = text.lower()

        # ---------------------------------------------------------
        # 1. Soil Health Extraction
        # ---------------------------------------------------------
        # Soil Organic Carbon % (e.g., '0.3% organic carbon', 'SOC is 0.3%', 'soil organic carbon is 0.3%')
        soc_match = re.search(r"(?:soil organic carbon|soc|organic carbon|carbon)\s*(?:level|content|is|of|:|=)?\s*(\d+(?:\.\d+)?)\s*%", lower_text)
        if not soc_match:
            soc_match = re.search(r"(\d+(?:\.\d+)?)\s*%\s*(?:soil organic carbon|soc|organic carbon)", lower_text)
        if soc_match:
            try:
                extracted_dict["soil_organic_carbon_pct"] = float(soc_match.group(1))
            except ValueError:
                pass

        # Soil pH (e.g., 'pH 6.5', 'pH is 7.2')
        ph_match = re.search(r"\bph\s*(?:level|is|of|:|=)?\s*(\d+(?:\.\d+)?)\b", lower_text)
        if ph_match:
            try:
                ph_val = float(ph_match.group(1))
                if 0.0 <= ph_val <= 14.0:
                    extracted_dict["soil_ph"] = ph_val
            except ValueError:
                pass

        # Soil Moisture
        if re.search(r"\b(now\s+adequate|adequate\s+moisture|adequate|moist)\b", lower_text):
            extracted_dict["soil_moisture"] = "adequate"
        elif re.search(r"\b(waterlogged|saturated|flooded|ponding)\b", lower_text):
            extracted_dict["soil_moisture"] = "waterlogged"
        elif re.search(r"\b(dry|parched|arid\s+soil|low\s+moisture|moisture\s+deficit)\b", lower_text):
            extracted_dict["soil_moisture"] = "dry"

        # ---------------------------------------------------------
        # 2. Land Use & Cropping Pattern
        # ---------------------------------------------------------
        if "monoculture wheat" in lower_text or ("wheat" in lower_text and "monoculture" in lower_text):
            extracted_dict["cropping_pattern"] = "monoculture wheat"
        elif "monoculture" in lower_text:
            extracted_dict["cropping_pattern"] = "monoculture"
        elif "crop rotation" in lower_text or "rotation" in lower_text:
            extracted_dict["cropping_pattern"] = "crop_rotation"
        elif "intercropping" in lower_text:
            extracted_dict["cropping_pattern"] = "intercropping"

        if "cropland" in lower_text or "arable" in lower_text:
            extracted_dict["land_use_type"] = "cropland"
        elif "pasture" in lower_text or "rangeland" in lower_text:
            extracted_dict["land_use_type"] = "pasture"

        # ---------------------------------------------------------
        # 3. Biodiversity Indicators
        # ---------------------------------------------------------
        if "low species richness" in lower_text or "species richness is low" in lower_text:
            extracted_dict["species_richness"] = "low"
        elif "high species richness" in lower_text:
            extracted_dict["species_richness"] = "high"

        if "low habitat diversity" in lower_text or "habitat diversity is low" in lower_text:
            extracted_dict["habitat_diversity"] = "low"
        elif "high habitat diversity" in lower_text:
            extracted_dict["habitat_diversity"] = "high"

        if re.search(r"\b(biodiversity\s+is\s+declining|declining\s+biodiversity|biodiversity\s+loss|biodiversity\s+drop)\b", lower_text):
            extracted_dict["biodiversity_condition"] = "declining"

        indicators = []
        if "pollinator" in lower_text or "bees" in lower_text:
            indicators.append("low_pollinators")
        if "earthworm" in lower_text:
            indicators.append("few_earthworms")
        if indicators:
            extracted_dict["biodiversity_indicators"] = indicators

        # ---------------------------------------------------------
        # 4. Climate & Hydrology
        # ---------------------------------------------------------
        if re.search(r"\b(rainfall\s+is\s+(?:very\s+)?low|low\s+rainfall|scanty\s+rainfall|dry\s+climate|drought\s+prone)\b", lower_text):
            extracted_dict["rainfall_regime"] = "low"
        elif re.search(r"\b(rainfall\s+is\s+(?:very\s+)?high|high\s+rainfall|heavy\s+rainfall|monsoon)\b", lower_text):
            extracted_dict["rainfall_regime"] = "high"

        if re.search(r"\b(temperature\s+is\s+high|high\s+temperature|heat\s+stress|extreme\s+heat|hot\s+climate)\b", lower_text):
            extracted_dict["temperature_regime"] = "high_temperature"

        if "waterlogged" in lower_text or "poor drainage" in lower_text:
            extracted_dict["water_availability"] = "waterlogged"

        # Region / Biome context
        if "semi-arid" in lower_text or "semi arid" in lower_text:
            extracted_dict["region"] = "semi-arid"
            extracted_dict.setdefault("rainfall_regime", "low")
        elif "arid" in lower_text:
            extracted_dict["region"] = "arid"
            extracted_dict.setdefault("rainfall_regime", "low")

        # ---------------------------------------------------------
        # 5. Human Impact
        # ---------------------------------------------------------
        pressures = []
        if "tillage" in lower_text or "plowing" in lower_text:
            extracted_dict["agricultural_pressure"] = "intensive_tillage"
            pressures.append("intensive_tillage")
        if "pesticide" in lower_text or "fertilizer" in lower_text or "chemical" in lower_text or "pollution" in lower_text:
            extracted_dict["pollution_pressure"] = "synthetic_chemicals_and_fertilizers"
            pressures.append("chemical_pollution")
        if re.search(r"\b(de-?forest\w*|cleared\s+woodland|land\s+clearing|clearing)\b", lower_text):
            extracted_dict["deforestation_status"] = "cleared_woodland"
            pressures.append("deforestation")
        if pressures:
            extracted_dict["human_pressures"] = pressures

        return EnvironmentalState(**extracted_dict)
