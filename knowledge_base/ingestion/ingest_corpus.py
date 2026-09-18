"""Corpus Ingestion Pipeline for Darukaa.Earth Biodiversity Knowledge Base.

Ingests scientific documents, verifies provenance, chunks text, and stores embeddings
into local ChromaDB vector store.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

base_dir = Path(__file__).resolve().parent.parent.parent
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

import chromadb
from knowledge_base.ingestion.chunker import chunk_document, DocumentChunk

CHROMA_COLLECTION_NAME = "biodiversity_knowledge"


def ingest_corpus(
    corpus_dir: Optional[Path] = None,
    db_dir: Optional[Path] = None,
    reset_collection: bool = True,
) -> Dict[str, Any]:
    """Ingests all documents in corpus_dir into ChromaDB vector store.
    
    Returns:
        Summary statistics dict with document count and chunk count.
    """
    base_dir = Path(__file__).resolve().parent.parent.parent
    corpus_path = corpus_dir or (base_dir / "knowledge_base" / "corpus")
    db_path = db_dir or (base_dir / "data" / "chroma_db")

    db_path.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(db_path))

    if reset_collection:
        try:
            client.delete_collection(name=CHROMA_COLLECTION_NAME)
        except Exception:
            pass

    collection = client.get_or_create_collection(
        name=CHROMA_COLLECTION_NAME,
        metadata={"description": "Peer-reviewed and institutional environmental science literature"}
    )

    doc_files = list(corpus_path.glob("*.md"))
    if not doc_files:
        raise FileNotFoundError(f"No markdown documents found in corpus directory: {corpus_path}")

    all_chunks: List[DocumentChunk] = []
    for doc_file in doc_files:
        chunks = chunk_document(doc_file)
        all_chunks.extend(chunks)

    # Ingest chunks into ChromaDB
    ids = [c.chunk_id for c in all_chunks]
    documents = [c.text for c in all_chunks]
    metadatas = [c.to_metadata_dict() for c in all_chunks]

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )

    summary = {
        "status": "success",
        "documents_ingested": len(doc_files),
        "chunks_indexed": len(all_chunks),
        "collection_name": CHROMA_COLLECTION_NAME,
        "storage_path": str(db_path),
    }
    return summary


if __name__ == "__main__":
    result = ingest_corpus()
    print("Ingestion complete:")
    for k, v in result.items():
        print(f"  {k}: {v}")
