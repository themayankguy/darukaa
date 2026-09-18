# Darukaa.Earth AI Biodiversity Intelligence Chatbot — System Requirements Specification

> Source Document: `Hackathon_Challenge__AI_Revised_861330.pdf` (`Hackathon_Challenge.pdf`)  
> Role: AI Environmental Scientist System (Depth of thinking, system design, scientific reasoning over UI-heavy apps)

---

## 1. Objective

Build an AI-powered conversational system that:
1. **Maintains a structured knowledge base** of biodiversity and environmental metrics.
2. **Understands user queries** about ecosystems, land, and climate conditions.
3. **Generates actionable, non-obvious recommendations** to improve biodiversity.
4. **Supports every recommendation** with scientific reasoning and empirical/scientific evidence.
5. **Behaves like an AI environmental scientist**, not a generic surface-level chatbot.

---

## 2. Core Requirements

### Requirement 1: Knowledge System (Critical)
The system must include a dedicated, retrievable knowledge layer—not merely prompt-engineered LLM memory.
- **Coverage Areas**:
  - **Soil Health**: pH, soil organic carbon (SOC %), moisture levels, microbial activity.
  - **Land Use / Land Cover (LULC)**: Cropland, monoculture, agroforestry, fallow, forest cover, habitat corridors.
  - **Biodiversity Indicators**: Species richness, Shannon-Wiener index, habitat diversity, pollinator support, trophic complexity.
  - **Climate Factors**: Temperature regimes, annual/seasonal rainfall patterns, drought frequency, aridity index.
  - **Human Impact**: Chemical pollution (pesticides, synthetic fertilizers), deforestation, soil compaction, habitat fragmentation.
- **System Architecture Expectation**:
  - Implement RAG (Retrieval-Augmented Generation), vector databases, embeddings, and/or structured environmental datasets.
  - Index credible research papers, institutional reports (e.g., FAO, IPCC), or scientific environmental datasets.
  - Clearly demonstrate and expose how knowledge is retrieved, scored, and used in downstream inference.

### Requirement 2: Conversational Intelligence
The conversational engine must act dynamically based on dialogue state and data completeness:
- **Clarifying Questions**: Proactively detect missing, underspecified, or ambiguous environmental inputs and prompt the user for specific parameters before finalizing recommendations.
- **Multi-Turn Memory**: Maintain session context across multiple dialogue turns, preserving previously supplied environmental parameters and user preferences.
- **Context Adaptation**: Adapt tone, depth, and specific mitigation strategies based on cumulative conversation context and domain constraints.

### Requirement 3: Evidence-Backed Recommendations (Mandatory)
Every suggested intervention must be grounded in peer-reviewed or institutional science. Each recommendation must include:
- **What to do**: Precise, non-generic operational intervention.
- **Why it works**: Detailed ecological and mechanistic scientific reasoning.
- **Which environmental metric improves**: Explicit, quantified or directional improvement in targeted parameters (e.g., SOC %, microbial biomass, water infiltration).
- **Reference to a study / report / model**: Explicit citation of credible institutional bodies or literature (e.g., FAO, IPCC, peer-reviewed agronomic/ecological studies).
- *Strict Benchmark*:
   - **Expected Quality**: *"Introduce legume-based cover crops → can improve soil organic carbon and microbial habitat while supporting pollinator resources, where the local evidence is relevant."*
  - **Unacceptable**: *"Use sustainable practices"* or generic boilerplate advice.

### Requirement 4: Multi-Metric Reasoning
The reasoning engine must analyze interconnected ecological dynamics rather than treating variables in isolation:
- Must connect multiple variables concurrently:
  - Soil health $\longleftrightarrow$ Biodiversity
  - Water availability $\longleftrightarrow$ Species survival
  - Land use $\longleftrightarrow$ Habitat fragmentation
- **Mandatory Constraint**: Must handle at least **3 environmental variables together** (no single-variable or dual-variable isolated answers). This represents the primary technical differentiator.

### Requirement 5: Input Handling
The system must support diverse modalities of environmental context ingestion:
- **Text Input** (Mandatory): Natural language queries and descriptions from users.
- **Structured Input** (Mandatory): JSON or structured key-value payloads containing numeric and categorical sensor/field data (e.g., SOC %, pH, annual rainfall, crop type, region).
- **Spatial / Geographic Context** (Bonus): Support for geo-coordinates or spatial context to infer regional ecological biomes, precipitation baselines, and soil orders.

### Requirement 6: Output Quality & Structure
Every system recommendation response must clearly provide:
- **Recommendation**: Concrete, non-obvious intervention strategy.
- **Impacted Metrics**: Specific environmental and biodiversity variables affected.
- **Time Horizon**: Categorized as Short-term, Medium-term, or Long-term.
- **Confidence Level**: Explicit confidence score or rating (optional in schema, but stated as high-value).

---

## 3. Detailed Sub-Requirements Breakdown

| Dimension | Sub-Requirement Details |
| :--- | :--- |
| **Knowledge Ingestion & Indexing** | • Ingest and index authoritative scientific literature (FAO reports, IPCC mitigation frameworks, peer-reviewed agroecology papers).<br>• Partition knowledge into chunked vector embeddings alongside structured taxonomies/knowledge graphs.<br>• Provide metadata tracking (source, author/institution, year, DOI/URL, metric category). |
| **Information Extraction & Parsing** | • Extract entities across all 5 mandatory domains (Soil, Land, Biodiversity, Climate, Human Impact).<br>• Parse both unstructured natural language statements and explicit structured JSON payloads.<br>• Validate extracted parameter ranges (e.g., pH $0-14$, SOC percentages, rainfall in mm/category). |
| **Completeness Assessment & Clarification** | • Check whether sufficient variables (minimum 3 interdependent variables) are present to form a scientifically sound diagnosis.<br>• If key baseline data is missing (e.g., user states only *"biodiversity is declining on my land"*), trigger a clarifying dialogue turn requesting specific missing metrics (SOC %, rainfall, land use type). |
| **Ecological Reasoning Engine** | • Synthesize retrieved scientific evidence with user-supplied parameters.<br>• Model multi-metric causal pathways (e.g., Semi-arid + Low rainfall + Low SOC 0.3% + Monoculture wheat $\rightarrow$ Agroforestry / Intercropping with drought-tolerant legumes $\rightarrow$ Microclimate dampening + Nitrogen fixation + Root exudates for mycorrhizal fungi). |
| **Structured Output Generation** | • Produce structured, readable outputs containing: Core recommendation, Scientific justification, Target impacted metrics, Quantifiable expected gains, Time horizon (Short/Medium/Long-term), Confidence rating, and Credible literature citations. |
| **Session Memory & State Tracking** | • Track conversational state, slot-filling history, and prior recommendations across multi-turn exchanges without losing context. |

---

## 4. Input Requirements

The system must accept and process two primary input formats, with one optional bonus format:

1. **Text Input (Mandatory)**
   - Unstructured conversational inputs (e.g., *"My farm in a semi-arid zone is facing severe topsoil erosion and crop yield drops under monoculture wheat."*).
   - Incomplete diagnostic statements requiring conversational follow-up (e.g., *"Biodiversity is declining on my land"*).

2. **Structured Input (Mandatory - JSON or Equivalent)**
   - Normalized key-value schema representing measured field parameters:
     ```json
     {
       "soil_organic_carbon_pct": 0.3,
       "soil_ph": 7.8,
       "rainfall_pattern": "low / semi-arid",
       "current_land_use": "monoculture wheat",
       "region": "semi-arid",
       "human_pressures": ["heavy tillage", "synthetic nitrogen overuse"],
       "coordinates": {"lat": 26.9124, "lng": 75.7873}
     }
     ```

3. **Spatial Context (Bonus)**
   - Latitude/Longitude coordinates or named geographic region enabling automated lookup of ecological biome, historical rainfall, and native biodiversity indicators.

---

## 5. Output Requirements

For each inquiry and scenario analysis, the system must output a structured, readable, and actionable response incorporating:

1. **Actionable Recommendation(s)**: Specific practice (e.g., agroforestry strip intercropping, multi-species legume cover cropping, windbreak hedgerow installation).
2. **Scientific Explanation / Why it Works**: Biological, physical, and chemical mechanisms (e.g., rhizobial nitrogen fixation, mycorrhizal hyphal networks, evaporation reduction via canopy microclimate).
3. **Impacted Metrics**: Explicit list of metrics improved (e.g., Soil Organic Carbon %, Infiltration Rate, Earthworm Density, Beneficial Insect Diversity).
4. **Quantifiable Improvement Estimates**: Measurable benchmarks derived from studies (e.g., `+15-25% SOC over 2-3 years`, `+40% pollinator abundance`).
5. **Time Horizon**: Clear categorization into Short-Term (< 1 year), Medium-Term (1–3 years), and Long-Term (> 3–5+ years).
6. **Confidence Level**: Estimated confidence level (High / Medium / Low or percentage score) based on retrieved evidence alignment and parameter completeness.
7. **Scientific Citations & Grounding**: Explicit attributions to recognized organizations (FAO, IPCC, IPBES) or specific published literature.

---

## 6. Evaluation Criteria & Weights

| Evaluation Dimension | Weight | Exact PDF Criteria |
| :--- | :---: | :--- |
| **Depth of Reasoning** | **30%** | • Are recommendations non-obvious?<br>• Do they combine multiple environmental variables concurrently? |
| **Scientific Grounding** | **25%** | • Are claims backed by credible sources (FAO, IPCC, etc.)?<br>• Is reasoning accurate, rigorous, and explainable? |
| **Knowledge System Design** | **20%** | • Use of RAG / vector DB / structured datasets.<br>• Clarity and robustness of the knowledge retrieval pipeline. |
| **Conversational Intelligence** | **15%** | • Context awareness.<br>• Intelligent follow-up questioning when inputs are incomplete.<br>• Multi-turn memory handling. |
| **Output Clarity** | **10%** | • Structured, readable, and actionable responses. |
| **Total** | **100%** | |

---

## 7. System Constraints

1. **No Generic LLM-Only Solutions**: Pure prompting without an explicit, verifiable, retrievable knowledge layer (RAG/embeddings/vector database/structured knowledge) is disqualified.
2. **No Shallow or Obvious Recommendations**: Generic platitudes (e.g., *"adopt sustainable agriculture"*, *"plant trees"*, *"reduce water use"*) are strictly unacceptable. Recommendations must specify species types, practices, quantitative mechanisms, and timescales.
3. **Multi-Metric Interdependency (Minimum 3 Variables)**: Every recommendation must demonstrate joint reasoning across at least **3 environmental variables simultaneously** (e.g., Soil Carbon + Rainfall Pattern + Cropping Regime $\rightarrow$ Biodiversity Outcome). Single-variable or isolated analyses fail the core test.
4. **Behavioral Persona**: The system must operate and communicate as an **AI Environmental Scientist**, not a generic conversational bot.
5. **No UI-Heavy Demands**: The primary evaluation focus is on **depth of thinking, system design, and scientific reasoning** rather than cosmetic visual presentation (though clean, intuitive access via CLI/API/Web demo is required).

---

## 8. Submission Requirements

1. **Format**: Exactly **one Word document (`.docx`)** submitted via the My Jobs / Applied Job page.
2. **Document Contents**:
   - **GitHub Repository Link** for the completed project.
   - **Live Demo URL** (where applicable).
   - **Brief `README.md` Overview** covering:
     - System Architecture
     - Database / Schema design
     - Local setup instructions
     - CI/CD details
   - **Access Credentials / Notes**: Any credentials, environment notes, or instructions necessary to run and test the submission.
3. **Repository Access Guidelines**:
   - If public: provide repository link only.
   - If private: explicitly grant access to:
     - `ankita.dasgupta@darukaa.com`
     - `harsh.kumar@darukaa.com`
     - `utkarsh.gauniyal@darukaa.com`
     - `guneet.mutreja@darukaa.com`

---

## 9. Acceptance Criteria for Our Implementation

To achieve maximum scores across all evaluation pillars, our implementation will fulfill the following verified criteria:

1. **Knowledge Retrieval Pipeline Verified**:
   - Real, curated environmental science corpus indexed in a vector store with semantic embeddings and structured metadata tags.
   - Transparent retrieval output displaying similarity scores, retrieved passages, and primary citations (FAO, IPCC, journal papers).
2. **Multi-Metric Co-Reasoning Engine (3+ Variables)**:
   - System takes inputs spanning soil health, climate, land use, hydrology, and human impact, evaluating their intersection rather than running independent prompts.
   - Verified on the benchmark test case:
     *Input*: SOC 0.3%, low rainfall, semi-arid, monoculture wheat.  
     *Output*: Specific agroforestry/intercropping intervention, mechanistic carbon/biodiversity impact, quantitative projection (15–25% SOC improvement over 2–3 years), and IPCC/FAO citations.
3. **Clarifying Question Loop**:
   - When fed vague prompts (e.g., *"Biodiversity is declining on my land"*), system rejects generic speculation and requests specific missing parameters (SOC %, rainfall, land use history, drainage).
4. **Multi-Turn Context & Session Memory**:
   - Dialogue preserves state across turns so user updates update the internal environmental profile iteratively.
5. **Dual Input Processing (Text & JSON)**:
   - CLI / API endpoints accept freeform text inquiries as well as structured JSON environmental state objects, with optional lat/long geolocation support.
6. **Structured Scientist-Grade Output**:
   - Standardized output schema containing: (a) Intervention, (b) Mechanistic scientific rationale, (c) Target metrics affected, (d) Estimated timeframe, (e) Quantified gain estimates, (f) Confidence score, (g) Exact scientific citations.
7. **Complete Submission Assets**:
   - Well-documented GitHub repository, clean `README.md`, automated tests, reproducible local execution, and compiled `.docx` submission report matching all required reviewer access configurations.
