"""CH21 Vector Databases: a self-contained Retrieval-Augmented Generation
(RAG) retrieval-pipeline sketch (Section 4.6).

Uses deterministic, hash-based pseudo-embeddings instead of a real ML model
so the example runs offline with no network access or model download --
the vector arithmetic (chunking, cosine similarity, top-k retrieval, prompt
assembly) is identical in shape to a production pipeline built on a real
embedding model and vector database.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

import numpy as np

EMBEDDING_DIMS = 64


def pseudo_embed(text: str) -> np.ndarray:
    """A deterministic stand-in for a real embedding model call.

    Hashes overlapping character n-grams into a fixed-size vector so that
    texts sharing substrings produce vectors with non-trivial cosine
    similarity -- enough to demonstrate the retrieval mechanics without
    depending on an external model.
    """
    vector = np.zeros(EMBEDDING_DIMS, dtype=np.float32)
    normalized = re.sub(r"\s+", " ", text.lower()).strip()
    for n in (3, 4, 5):
        for i in range(len(normalized) - n + 1):
            gram = normalized[i:i + n]
            digest = hashlib.sha256(gram.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % EMBEDDING_DIMS
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign
    norm = np.linalg.norm(vector)
    return vector / norm if norm > 0 else vector


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(a @ b)  # both already unit-normalized by pseudo_embed


def chunk_document(text: str, chunk_size: int = 200, overlap: int = 40) -> list[str]:
    """Fixed-size chunking with overlap (Section 4.6): overlap ensures a
    single fact near a chunk boundary is not the sole copy in only one
    chunk, mitigating the boundary-splitting failure mode from Section
    4.6's scenario."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        if end >= len(words):
            break
        start = end - overlap
    return chunks


@dataclass
class VectorStore:
    """A minimal in-memory vector store standing in for a real vector
    database's ingestion/query interface (Section 5)."""

    chunk_texts: list[str]
    chunk_vectors: list[np.ndarray]
    source_documents: list[str]

    @classmethod
    def build(cls) -> "VectorStore":
        return cls(chunk_texts=[], chunk_vectors=[], source_documents=[])

    def upsert(self, document_id: str, text: str) -> None:
        for chunk in chunk_document(text):
            self.chunk_texts.append(chunk)
            self.chunk_vectors.append(pseudo_embed(chunk))
            self.source_documents.append(document_id)

    def search(self, query: str, k: int = 3) -> list[tuple[str, str, float]]:
        query_vector = pseudo_embed(query)
        scored = [
            (self.source_documents[i], self.chunk_texts[i], cosine_similarity(query_vector, vector))
            for i, vector in enumerate(self.chunk_vectors)
        ]
        scored.sort(key=lambda item: -item[2])
        return scored[:k]


def build_grounded_prompt(question: str, retrieved_chunks: list[tuple[str, str, float]]) -> str:
    """Assemble an LLM prompt from the question plus retrieved context,
    the query-time half of the Section 4.6 RAG sequence diagram."""
    context_blocks = "\n\n".join(
        f"[Source: {doc_id}]\n{chunk}" for doc_id, chunk, _score in retrieved_chunks
    )
    return (
        "Answer the question using ONLY the context below. "
        "If the context does not contain the answer, say so.\n\n"
        f"Context:\n{context_blocks}\n\n"
        f"Question: {question}\n"
        "Answer:"
    )


def demo() -> None:
    store = VectorStore.build()
    store.upsert(
        "policy-handbook.md",
        "Employees may not expense personal travel under the standard "
        "reimbursement policy. Except in cases of an approved business "
        "relocation, personal travel costs during a relocation window are "
        "reimbursable up to the relocation allowance cap.",
    )
    store.upsert(
        "onboarding-guide.md",
        "New hires receive a laptop, a badge, and access to the internal "
        "wiki during their first week. Managers should schedule a 30 day "
        "check-in to review onboarding progress.",
    )

    question = "Can an employee expense personal travel during a relocation?"
    retrieved = store.search(question, k=2)

    print("Retrieved chunks (Section 4.6 query-time retrieval):")
    for doc_id, chunk, score in retrieved:
        print(f"  score={score:.3f} source={doc_id}\n    {chunk[:90]}...")

    prompt = build_grounded_prompt(question, retrieved)
    print("\nAssembled grounded prompt (would be sent to the generative LLM):\n")
    print(prompt)


if __name__ == "__main__":
    demo()
