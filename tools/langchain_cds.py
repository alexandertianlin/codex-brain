from __future__ import annotations

import sqlite3
from pathlib import Path

try:
    from langchain_core.documents import Document
except Exception:  # pragma: no cover - fallback for environments without LangChain
    Document = None  # type: ignore


CDS_DB = Path(r"D:\agiletact\codex-memory\index\memory.sqlite")


def load_cds_documents(limit: int | None = None):
    """Load CDS memories as LangChain Document objects.

    This is the bridge from the user's local CDS memory into the LangChain ecosystem.
    It intentionally reads the existing CDS SQLite store instead of creating a second
    memory system.
    """
    if Document is None:
        raise RuntimeError("langchain-core is not installed in this Python environment")
    conn = sqlite3.connect(str(CDS_DB))
    conn.row_factory = sqlite3.Row
    sql = """
        SELECT id, title, project, tags, risk, status, body, evidence,
               memory_type, importance, recurrence, confidence, retrieval_priority,
               useful_count, noise_count, updated_at
        FROM memories
        WHERE status != 'archived'
        ORDER BY retrieval_priority DESC, useful_count DESC, updated_at DESC
    """
    if limit:
        sql += " LIMIT ?"
        rows = conn.execute(sql, (limit,)).fetchall()
    else:
        rows = conn.execute(sql).fetchall()
    docs = []
    for row in rows:
        metadata = {key: row[key] for key in row.keys() if key not in {"body", "evidence"}}
        content = f"{row['title']}\n\n{row['body']}\n\nEvidence: {row['evidence'] or ''}".strip()
        docs.append(Document(page_content=content, metadata=metadata))
    conn.close()
    return docs


def print_sample(limit: int = 5) -> None:
    docs = load_cds_documents(limit=limit)
    for doc in docs:
        print(f"#{doc.metadata['id']} {doc.metadata['title']} priority={doc.metadata['retrieval_priority']}")


if __name__ == "__main__":
    print_sample()
