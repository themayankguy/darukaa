"""Tests for scientific corpus ingestion and semantic retriever.

Verifies:
- Test 5: Evidence provenance (source_id, title, publication metadata, URL/DOI, traceability)
- Semantic retrieval precision
- Topic filtering
"""

import pytest
from pathlib import Path
from src.knowledge.retriever import ScientificRetriever, RetrievedEvidenceChunk


@pytest.fixture
def retriever():
    return ScientificRetriever()


def test_retriever_returns_results(retriever):
    """Verifies that vector search returns relevant chunks."""
    chunks = retriever.retrieve(query="legume intercropping soil organic carbon semi-arid", top_k=3)
    assert len(chunks) > 0
    top = chunks[0]
    assert isinstance(top, RetrievedEvidenceChunk)
    assert top.similarity_score > 0.0
    assert len(top.excerpt) > 20


def test_evidence_provenance_integrity(retriever):
    """Test 5: Retrieve an evidence chunk and assert full bibliographic provenance."""
    chunks = retriever.retrieve(query="agroforestry microclimate wind speed cooling", top_k=2)
    assert len(chunks) > 0

    chunk = chunks[0]
    # Mandatory provenance assertions
    assert chunk.source_id in ["ipcc_srccl_ch3_2019", "kuyper_agroforestry_2020", "fao_rec_soils_2020"]
    assert len(chunk.source_title) > 5
    assert len(chunk.source_organization) > 2
    assert chunk.publication_year >= 2015
    assert chunk.source_url_or_doi.startswith("http") or "doi.org" in chunk.source_url_or_doi
    assert len(chunk.provenance_note) > 0
    assert chunk.chunk_id.startswith(chunk.source_id)


def test_retriever_topic_filtering(retriever):
    """Verifies that metadata topic filtering narrows down retrieved literature."""
    chunks = retriever.retrieve(
        query="pollinator floral hedgerow",
        top_k=3,
        topic_filter="pollinator_forage_hedgerows_pesticide_impact"
    )
    assert len(chunks) > 0
    for c in chunks:
        assert c.topic == "pollinator_forage_hedgerows_pesticide_impact"
        assert c.source_id == "ipbes_pollination_2016"
