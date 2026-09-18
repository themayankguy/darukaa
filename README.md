# Darukaa AI Environmental Scientist

## Project
Darukaa is an AI environmental decision-support system combining structured environmental state, multi-metric reasoning, scientific retrieval, and evidence-backed recommendations.

## Architecture

User Input -> Environmental State -> Clarification -> Condition Detection -> Multi-Metric Reasoning -> Candidate Intervention -> Scientific Retrieval -> Evidence Validation -> Recommendation

## Key Features

- Natural language input
- Structured JSON input
- Clarifying questions
- Multi-turn memory
- Multi-metric reasoning
- Local RAG knowledge layer
- Evidence-backed recommendations
- Scientific provenance
- Structured reasoning trace

## Technology

Backend: Python, FastAPI, Pydantic, ChromaDB, sentence-transformers, SQLite

Frontend: React, TypeScript, Tailwind, Vite

## Scientific Safeguards

- Ecological relationships are deterministic.
- Recommendations require relevant retrieved evidence.
- Unsupported quantitative claims are removed or downgraded to qualitative wording.
- Insufficient evidence is surfaced explicitly.
- The LLM does not invent scientific relationships, evidence, citations, or numbers.

## Running Locally

From the repository root:

```bash
python3 -m pytest -q
python3 -m src.main
```

Build the frontend:

```bash
cd frontend
npm install
npm run build
npm run dev
```

The backend serves the API at `http://localhost:8000`. The Vite frontend uses the configured API proxy during development.

## API

- `GET /api/v1/health`
- `POST /api/v1/chat`
- `POST /api/v1/assessment`
- `GET /api/v1/session/{session_id}`
- `GET /docs`

## Demo

Use:

> Wheat farmland in a semi-arid region. SOC 0.3%, low rainfall, monoculture wheat, low habitat diversity.

## Limitations

The local corpus consists of curated summaries rather than demonstrated verbatim extracts of the original publications. Independent source verification remains incomplete. See [docs/SOURCE_VERIFICATION.md](docs/SOURCE_VERIFICATION.md) for corrected metadata, removed quantitative claims, and remaining verification requirements.

## Testing

Final backend result: **31 passed, 0 failed, 0 skipped**.
