"""Targeted clarification engine for incomplete environmental profiles."""

from typing import Dict, List, Tuple, Optional, Any
from src.input_layer.schemas import EnvironmentalState
from src.core.llm_interface import LLMClient


class ClarificationEngine:
    """Evaluates multi-metric completeness and generates targeted clarification questions."""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client

    def evaluate_completeness(self, state: EnvironmentalState) -> Tuple[bool, List[str], str]:
        """Evaluates whether state has sufficient variables across domains for co-reasoning.
        
        Returns:
            Tuple of (is_complete, missing_variables_list, clarification_question_text)
        """
        supplied = state.get_supplied_variables()
        active_domains = state.get_supplied_domains()

        # Rule: Needs at least 3 distinct variables spanning at least 2 distinct domains
        if len(supplied) >= 3 and len(active_domains) >= 2:
            return True, [], ""

        # Identify complementary missing factors based on what's already present
        missing_suggestions: List[str] = []
        
        if "soil_health" not in active_domains:
            missing_suggestions.append("soil organic carbon % or soil moisture condition")
        if "climate" not in active_domains:
            missing_suggestions.append("rainfall regime or annual precipitation")
        if "land_use_cover" not in active_domains:
            missing_suggestions.append("cropping pattern (e.g., monoculture vs crop rotation)")
        if "biodiversity" not in active_domains and len(missing_suggestions) < 3:
            missing_suggestions.append("habitat diversity or observed pollinator presence")

        # Pick smallest useful set (at most 3 items)
        selected_missing = missing_suggestions[:3]

        # Generate targeted question
        supplied_desc = ", ".join([f"{k} = {v}" for k, v in supplied.items()])
        if supplied:
            question = (
                f"I have recorded your current environmental parameters ({supplied_desc}). "
                f"To establish the ecological interactions and provide an evidence-backed assessment, "
                f"could you provide at least one additional factor such as: {', '.join(selected_missing)}?"
            )
        else:
            question = (
                "To assess your land's biodiversity and ecosystem health, I need a few baseline environmental factors. "
                "Could you share your approximate soil organic carbon %, rainfall pattern, and current land use or cropping regime?"
            )

        # Optional LLM polish if available
        if self.llm:
            try:
                system_prompt = (
                    "You are an expert AI Environmental Scientist. Rephrase this targeted clarification question "
                    "politely and concisely. Do NOT answer the query, only ask for the missing factors."
                )
                polished = self.llm.generate(prompt=question, system_instruction=system_prompt)
                if polished and len(polished.strip()) > 10:
                    question = polished.strip()
            except Exception:
                pass

        return False, selected_missing, question
