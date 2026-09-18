"""Retriever for the Darukaa.Earth Scientific Knowledge Base.

Performs semantic similarity retrieval over ChromaDB while preserving full source provenance.
Supports domain filtering and configurable top-k without hardcoded distance barriers.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
import chromadb


class RetrievedEvidenceChunk(BaseModel):
    """An individual retrieved chunk retaining complete source provenance."""
    chunk_id: str
    source_id: str
    source_title: str
    source_organization: str
    publication_year: int
    source_type: str
    source_url_or_doi: str
    topic: str
    section_header: str
    excerpt: str
    similarity_score: float = Field(..., description="Cosine similarity score (0.0 to 1.0, higher is more similar).")
    distance: float = Field(..., description="Raw distance metric from vector database.")
    is_quantitative: bool = False
    variables_supported: List[str] = Field(default_factory=list)
    interventions_supported: List[str] = Field(default_factory=list)
    provenance_note: str = ""


class ScientificRetriever:
    """Semantic vector retriever over the curated scientific corpus."""

    def __init__(
        self,
        db_dir: Optional[Path] = None,
        collection_name: str = "biodiversity_knowledge",
        client: Optional[chromadb.ClientAPI] = None,
    ):
        base_dir = Path(__file__).resolve().parent.parent.parent
        self.db_dir = db_dir or (base_dir / "data" / "chroma_db")
        self.collection_name = collection_name

        if client:
            self.client = client
        else:
            self.client = chromadb.PersistentClient(path=str(self.db_dir))
        
        self.collection = self.client.get_or_create_collection(name=self.collection_name)

    def retrieve(
        self,
        query: str,
        top_k: int = 4,
        topic_filter: Optional[str] = None,
        intervention_id: Optional[str] = None,
    ) -> List[RetrievedEvidenceChunk]:
        """Retrieves top-k evidence passages matching the query with optional metadata filtering."""
        where_clause = None
        if topic_filter:
            where_clause = {"topic": topic_filter}

        requested_results = top_k * 3 if intervention_id else top_k
        query_params: Dict[str, Any] = {
            "query_texts": [query],
            "n_results": min(requested_results, max(1, self.collection.count() or 1)),
        }
        if where_clause:
            query_params["where"] = where_clause

        try:
            results = self.collection.query(**query_params)
        except Exception as e:
            # Return empty if query fails or collection is empty
            return []

        if not results or not results["documents"] or len(results["documents"][0]) == 0:
            return []

        retrieved_chunks: List[RetrievedEvidenceChunk] = []
        docs = results["documents"][0]
        metadatas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
        distances = results["distances"][0] if results.get("distances") else [0.5] * len(docs)
        ids = results["ids"][0] if results.get("ids") else [f"chunk_{i}" for i in range(len(docs))]

        for doc_text, meta, dist, cid in zip(docs, metadatas, distances, ids):
            # ChromaDB cosine distance range is [0, 2]; convert to similarity: sim = 1.0 - (dist / 2.0)
            similarity = max(0.0, min(1.0, 1.0 - (float(dist) / 2.0)))
            
            var_list = [v.strip() for v in meta.get("variables_supported", "").split(",") if v.strip()]
            int_list = [i.strip() for i in meta.get("interventions_supported", "").split(",") if i.strip()]

            chunk = RetrievedEvidenceChunk(
                chunk_id=cid,
                source_id=str(meta.get("source_id", "unknown_source")),
                source_title=str(meta.get("title", "Untitled Source")),
                source_organization=str(meta.get("organization", "Unknown Organization")),
                publication_year=int(meta.get("publication_year", 2020)),
                source_type=str(meta.get("source_type", "literature")),
                source_url_or_doi=str(meta.get("original_url_or_doi", "")),
                topic=str(meta.get("topic", "")),
                section_header=str(meta.get("section_header", "")),
                excerpt=doc_text,
                similarity_score=round(similarity, 4),
                distance=round(float(dist), 4),
                is_quantitative=bool(meta.get("is_quantitative", False)),
                variables_supported=var_list,
                interventions_supported=int_list,
                provenance_note=str(meta.get("provenance_note", "")),
            )
            retrieved_chunks.append(chunk)

        if intervention_id:
            retrieved_chunks = [
                chunk for chunk in retrieved_chunks
                if intervention_id in chunk.interventions_supported
            ]

        return retrieved_chunks[:top_k]
