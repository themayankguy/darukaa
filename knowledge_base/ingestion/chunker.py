"""Scientific document chunker with strict source provenance preservation.

Parses YAML frontmatter metadata and chunks text preserving full bibliographic
and domain metadata across all downstream evidence chunks.
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    """An individual text chunk retaining full parent document provenance."""
    chunk_id: str = Field(..., description="Unique chunk identifier, e.g. fao_rec_soils_2020_chunk_1")
    source_id: str
    title: str
    organization: str
    publication_year: int
    source_type: str
    original_url_or_doi: str
    topic: str
    variables_supported: List[str]
    interventions_supported: List[str]
    provenance_note: str
    section_header: str
    text: str
    is_quantitative: bool = False

    def to_metadata_dict(self) -> Dict[str, Any]:
        """Converts chunk metadata into ChromaDB-compatible primitive dictionary."""
        return {
            "source_id": self.source_id,
            "title": self.title,
            "organization": self.organization,
            "publication_year": self.publication_year,
            "source_type": self.source_type,
            "original_url_or_doi": self.original_url_or_doi,
            "topic": self.topic,
            "section_header": self.section_header,
            "is_quantitative": self.is_quantitative,
            "variables_supported": ",".join(self.variables_supported),
            "interventions_supported": ",".join(self.interventions_supported),
            "provenance_note": self.provenance_note,
        }


def parse_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
    """Extracts YAML frontmatter and body text from markdown."""
    frontmatter_pattern = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
    match = frontmatter_pattern.match(content)
    if not match:
        raise ValueError("Corpus document is missing mandatory YAML frontmatter with provenance metadata.")
    
    yaml_text = match.group(1)
    body = content[match.end():].strip()

    metadata: Dict[str, Any] = {}
    current_list_key = None

    for line in yaml_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        
        # Check list item
        if line.startswith("- ") and current_list_key:
            item_val = line[2:].strip().strip('"').strip("'")
            metadata[current_list_key].append(item_val)
            continue

        # Check key-value
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip()
            if not val:
                metadata[key] = []
                current_list_key = key
            else:
                current_list_key = None
                val = val.strip('"').strip("'")
                if key == "publication_year":
                    metadata[key] = int(val)
                else:
                    metadata[key] = val

    # Validate mandatory provenance fields
    mandatory_fields = [
        "source_id", "title", "organization", "publication_year",
        "source_type", "original_url_or_doi", "topic"
    ]
    for field in mandatory_fields:
        if field not in metadata:
            raise ValueError(f"Mandatory provenance field '{field}' is missing in frontmatter.")

    return metadata, body


def chunk_document(file_path: Path) -> List[DocumentChunk]:
    """Chunks a curated scientific markdown document preserving full provenance metadata."""
    content = file_path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(content)

    # Split by section headers (Markdown H1/H2/H3)
    section_pattern = re.compile(r"(^|\n)(#{1,3}\s+[^\n]+)", re.MULTILINE)
    splits = section_pattern.split(body)

    chunks: List[DocumentChunk] = []
    current_header = "Introduction"
    chunk_index = 0

    # Number detector for quantitative verification
    quantitative_pattern = re.compile(r"\b\d+(\.\d+)?%|\b\d+–\d+%|\b\d+-\d+%\b")

    for i in range(len(splits)):
        part = splits[i].strip()
        if not part:
            continue
        if part.startswith("#"):
            current_header = part.lstrip("#").strip()
            continue

        # Split long sections into paragraphs if needed
        paragraphs = [p.strip() for p in part.split("\n\n") if p.strip()]
        for para in paragraphs:
            if len(para) < 50:  # Skip trivial headings or short snippets
                continue
            
            chunk_index += 1
            has_numbers = bool(quantitative_pattern.search(para))
            
            chunk = DocumentChunk(
                chunk_id=f"{meta['source_id']}_chunk_{chunk_index}",
                source_id=meta["source_id"],
                title=meta["title"],
                organization=meta["organization"],
                publication_year=meta["publication_year"],
                source_type=meta["source_type"],
                original_url_or_doi=meta["original_url_or_doi"],
                topic=meta["topic"],
                variables_supported=meta.get("variables_supported", []),
                interventions_supported=meta.get("interventions_supported", []),
                provenance_note=meta.get("provenance_note", ""),
                section_header=current_header,
                text=para,
                is_quantitative=has_numbers,
            )
            chunks.append(chunk)

    return chunks
