# Darukaa.Earth AI Biodiversity Intelligence System — MVP Scope Specification

> **Target Timeline**: 1-Day Delivery MVP  
> **Core Focus**: Depth of scientific reasoning, explicit multi-metric ecological interdependencies, and strict evidence grounding.

---

## 1. What is Implemented

1. **Input Ingestion & Entity Extraction**:
   - Natural language dialogue input parsing and typed JSON payload ingestion (`/api/v1/chat`, `/api/v1/chat/structured`).
   - Extraction of environmental parameters across 5 core domains: Soil Health, Land Use / Cover, Biodiversity Indicators, Climate / Hydrology, and Human Impact.
   - Validation of physical bounds using Pydantic v2 schemas.
   - Support for geo-coordinates / regional biome tagging.

2. **Conversational Intelligence & Slot-Filling Memory**:
   - Session tracking backed by local SQLite (`sessions.db`).
   - Cumulative Environmental Profile accumulator preserving variables across turns.
   - **Gated Multi-Metric Assessment**: When fewer than 3 environmental variables are available, the system identifies which variables are currently available, notes the missing variables, and formulates targeted, polite clarifying questions.
   - Multi-turn resumption: when the user provides the missing variable(s), the system merges context and proceeds directly to full ecological co-reasoning.

3. **Deterministic Environmental Reasoning Engine**:
   - **Decoupled from LLM**: Condition detection, cross-variable coupling, and candidate intervention selection are handled by a deterministic, rule-and-ontology-based engine.
   - Explicit structured relationships modeling the intersection of $\ge 3$ variables (e.g., Soil Carbon $\leftrightarrow$ Arid Rainfall $\leftrightarrow$ Monoculture Cropping).
   - Candidate intervention selector matching diagnosed conditions to viable agroecological practices.

4. **Curated Scientific Knowledge Base & Vector Retrieval**:
   - Curated corpus of authoritative scientific literature (FAO soils manuals, IPCC SRCCL land degradation chapters, peer-reviewed agroforestry/biodiversity syntheses).
   - Strict source provenance metadata (`source_id`, `title`, `organization`, `publication_year`, `source_type`, `original_url_or_doi`, `provenance_note`).
   - Clear distinction between:
     1. Original scientific source
     2. Curated local extraction / notes
     3. Retrieved evidence chunks
   - Local ChromaDB vector store with `sentence-transformers/all-MiniLM-L6-v2`.
   - Semantic retrieval with configurable similarity score and domain metadata filtering.

5. **Evidence Engine & Grounding Guardrails**:
   - Relevance evaluation mapping candidate interventions directly to retrieved text chunks.
   - **Zero-Tolerance Hallucination Guardrail**: Quantitative estimates (e.g., *"+15–25% SOC"*) are emitted **only if** explicitly present in retrieved text. If evidence is purely qualitative, recommendations state the qualitative directional mechanism without fabricated numbers.
   - **Insufficient Evidence Fallback**: When no retrieved passage exceeds relevance criteria, the system returns an explicit *"Insufficient scientific evidence in current corpus"* notice rather than hallucinating advice.

6. **Explainability & Structured Output**:
   - Standardized `ChatResponse` JSON containing environmental state, detected conditions, variable relationships, recommendations, impacted metrics, time horizon, confidence, evidence citations, and limitations.
   - **Structured Reasoning Trace**: Complete audit trail showing input factors, detected conditions, cross-variable relationships, candidate interventions, retrieved evidence, validated claims, and decision rationale. (No private chain-of-thought tokens exposed).

7. **Clean Local Testing & Demonstration Interface**:
   - FastAPI REST API with interactive Swagger docs (`/docs`).
   - Clean CLI runner for demonstration and verification.
   - Comprehensive `pytest` test suite verifying conversational flows, multi-metric reasoning, evidence grounding, and schema conformance.

---

## 2. What is Intentionally NOT Implemented

To ensure robust local execution, zero operational fragility, and delivery within the one-day hackathon timeframe, the following are intentionally excluded:
- **No Microservices or Service Meshes**: Single, modular Python codebase; runs anywhere in one process.
- **No Kubernetes, Docker Swarms, or Cloud Infrastructure**: Designed for instant local execution via Python venv.
- **No Neo4j or Heavy Graph Databases**: Cross-variable relationships are modeled natively in structured Python/JSON relationship definitions, achieving full explainability without database overhead.
- **No ML Model Training or Fine-Tuning**: No GPUs, no training runs, no loss functions, no weight checkpoints.
- **No Large Uncurated Web Scrapes / Heavy Datasets**: A focused, high-authority curated scientific corpus replaces massive unvetted data dumps.
- **No Complex GIS / Map Tile Servers**: Spatial context is handled via coordinate bounding boxes and biome attributes, not GIS raster pipelines.
- **No Authentication / Multi-Tenancy / OAuth**: Focus is entirely on scientific intelligence and conversational reasoning.
- **No Multiple LLM Provider Zoo**: Abstract `LLMClient` interface with one production provider (Gemini) and an offline `MockLLMClient` for fast local testing.

---

## 3. How the System Satisfies the Challenge

The Darukaa.Earth challenge explicitly prioritizes **depth of thinking, system design, and scientific reasoning over UI-heavy applications**. The system satisfies every dimension:

1. **Behaves as an Environmental Scientist (Not a Chatbot)**:
   - Uses domain ontology to diagnose environmental stress states rather than asking an LLM to "pretend to be an ecologist".
   - Demands minimum environmental context ($\ge 3$ variables) before making ecological recommendations.
2. **True Knowledge Grounding (Not Prompt Guessing)**:
   - Grounded in vetted FAO, IPCC, and peer-reviewed agroecological literature indexed with vector embeddings and full provenance metadata.
3. **Multi-Metric Interdependency**:
   - Rejects single-variable silos. Connects soil carbon deficits with rainfall moisture limits and monoculture biodiversity loss into a unified intervention.
4. **Transparent Explainability**:
   - Evaluators can inspect the exact reasoning trace showing every decision stage from raw inputs to validated citations.

---

## 4. Why No Conventional ML Training Dataset is Required

1. **Nature of the Problem**:
   - Environmental mitigation and biodiversity restoration are governed by **established ecological, biological, and physical laws** documented in scientific literature (e.g., nitrogen fixation rates, soil organic matter decomposition kinetics, microbial colonization of root zones).
   - Training a traditional machine learning model (e.g., a regression model or classifier) would require tens of thousands of labeled agricultural trial datasets, which are noisy, geographically idiosyncratic, and prone to spurious correlations.
2. **The Power of Knowledge Retrieval (RAG) over Model Training**:
   - Instead of trying to "bake" agricultural facts into static model weights via expensive and hallucination-prone fine-tuning, the system utilizes a **retrievable scientific knowledge layer**.
   - This approach matches the state-of-the-art in scientific AI: decoupling foundational language comprehension from factual, verifiable scientific domain knowledge.
3. **Auditability & Provenance**:
   - A trained black-box model cannot cite page numbers or institutional methodologies. A RAG and rule-grounded architecture provides immutable, auditable citations back to specific FAO and IPCC publications.

---

## 5. How Evidence Grounding Prevents Unsupported Recommendations

1. **Decoupled Architecture**:
   - The LLM does not decide what interventions are valid. The deterministic relationship rules select candidates based on diagnosed multi-variable conditions.
2. **Evidence Verification Gate**:
   - For every candidate intervention, the system queries ChromaDB for supporting scientific passages.
   - If the relevance score fails to meet the configurable threshold, or if no passages support the practice, the candidate is discarded or flagged as unsupported.
3. **Zero Numerical Hallucination Policy**:
   - If an intervention states a numerical outcome (e.g., *"increases SOC by 15–25%"*), the `EvidenceEngine` strictly verifies that this exact figure or range appears verbatim in the retrieved source text.
   - If the source only describes qualitative improvements (*"enhances microbial respiration and improves soil aggregation"*), the system emits only the qualitative mechanism.
4. **Explicit Failure Mode**:
   - If a user inquires about an ecological scenario not covered by the indexed corpus, the system explicitly outputs: `"Insufficient evidence in scientific knowledge base"` rather than guessing.
