#!/usr/bin/env python3
"""Interactive Terminal CLI Demo for Darukaa.Earth AI Biodiversity System.

Uses the exact same ChatOrchestrator pipeline as the REST API.
Demonstrates multi-turn memory, targeted clarifying questions, and evidence-backed recommendations.
"""

import sys
import uuid
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

from src.conversation.orchestrator import ChatOrchestrator


def main():
    print("=" * 80)
    print("DARUKAA.EARTH — AI BIODIVERSITY INTELLIGENCE SCIENTIST CLI")
    print("=" * 80)
    print("Type your environmental scenario below (or 'exit' / 'quit' to end).")
    print("Type 'reset' to start a new session.\n")

    orchestrator = ChatOrchestrator()
    session_id = str(uuid.uuid4())
    print(f"[*] Started Session: {session_id[:8]}...\n")

    while True:
        try:
            user_input = input("USER > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "q"]:
                print("\nSession ended. Thank you!")
                break
            if user_input.lower() == "reset":
                session_id = str(uuid.uuid4())
                print(f"\n[*] Started New Session: {session_id[:8]}...\n")
                continue

            response = orchestrator.process_chat(message=user_input, session_id=session_id)

            print("\nSYSTEM >")
            if response.status == "needs_clarification":
                print(f"[CLARIFICATION REQUIRED]")
                print(f"{response.clarification_question}\n")
                print(f"Current recorded parameters: {response.environmental_state}")
                print(f"Missing factors suggested: {response.missing_information}\n")
            else:
                print(f"[STATUS: COMPLETE EVIDENCE-BACKED ASSESSMENT]")
                print(f"Current State: {response.environmental_state}")
                print(f"Detected Conditions: {', '.join(response.detected_conditions or [])}\n")
                
                print("RECOMMENDATIONS:")
                for i, rec in enumerate(response.recommendations or [], 1):
                    print(f"\n  {i}. {rec.action} (Confidence: {rec.confidence})")
                    print(f"     • Why it Works: {rec.why_it_works}")
                    print(f"     • Impacted Metrics: {', '.join(rec.impacted_metrics)}")
                    print(f"     • Time Horizon: {rec.time_horizon}")
                    if rec.quantitative_estimate:
                        print(f"     • Quantitative Benchmark: \"{rec.quantitative_estimate}\"")
                    if rec.limitations:
                        print(f"     • Trade-offs / Limitations: {'; '.join(rec.limitations)}")
                    
                    print(f"     • Supporting Scientific Evidence ({len(rec.evidence)} sources):")
                    for chunk in rec.evidence[:2]:
                        print(f"       - [{chunk.source_id}] {chunk.source_title} ({chunk.publication_year})")
                        print(f"         DOI: {chunk.source_url_or_doi}")

                if response.reasoning_trace:
                    print(f"\nAUDIT REASONING TRACE:")
                    print(f"  • Triggered Rules: {', '.join(response.reasoning_trace.cross_variable_relationships)}")
                    print(f"  • Decision Rationale: {response.reasoning_trace.decision_rationale}\n")

            print("-" * 80 + "\n")

        except (KeyboardInterrupt, EOFError):
            print("\nExiting CLI. Goodbye!")
            break


if __name__ == "__main__":
    main()
