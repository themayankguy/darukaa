"""FastAPI Application for the Darukaa.Earth AI Biodiversity Intelligence System.

Exposes REST endpoints for natural-language chat, structured environmental assessment,
session history inspection, and service health.
"""

from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware

from src.input_layer.schemas import EnvironmentalState
from src.input_layer.response_schemas import ChatRequest, SystemResponse
from src.conversation.orchestrator import ChatOrchestrator
from src.conversation.session_manager import SessionManager

app = FastAPI(
    title="Darukaa.Earth AI Biodiversity Intelligence System",
    description="Knowledge-driven conversational AI environmental scientist providing evidence-backed, multi-metric biodiversity assessments.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware for local frontend and testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global orchestrator singleton
orchestrator = ChatOrchestrator()


@app.get("/api/v1/health", summary="Health Check")
def health_check() -> Dict[str, str]:
    """Returns service health status."""
    return {"status": "ok"}


@app.post("/api/v1/chat", response_model=SystemResponse, summary="Conversational Assessment")
def chat_endpoint(request: ChatRequest) -> SystemResponse:
    """Conversational endpoint accepting natural language environmental descriptions.
    Tracks session history and asks targeted clarifying questions when information is incomplete.
    """
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    
    return orchestrator.process_chat(
        message=request.message,
        session_id=request.session_id,
    )


@app.post("/api/v1/assessment", response_model=SystemResponse, summary="Structured Assessment")
def assessment_endpoint(
    state: EnvironmentalState,
    session_id: Optional[str] = None,
) -> SystemResponse:
    """Direct structured assessment endpoint accepting typed EnvironmentalState.
    Executes the exact same deterministic reasoning and evidence retrieval pipeline.
    """
    return orchestrator.process_assessment(
        state=state,
        session_id=session_id,
    )


@app.get("/api/v1/session/{session_id}", summary="Get Session History & Profile")
def get_session_endpoint(session_id: str = Path(..., description="Unique session ID")) -> Dict[str, Any]:
    """Retrieves cumulative environmental profile and conversation turns for a session."""
    session = orchestrator.session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    
    return {
        "session_id": session.session_id,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
        "turn_count": session.turn_count,
        "cumulative_state": session.cumulative_state.get_supplied_variables(),
        "history": [t.model_dump() for t in session.history],
    }
