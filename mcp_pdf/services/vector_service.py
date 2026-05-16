import json
import pickle
from pathlib import Path

import faiss
import numpy as np

VECTOR_STORE_PATH = Path("./vector_store")
INDEX_FILE = VECTOR_STORE_PATH / "faiss.index"
DOCUMENTS_FILE = VECTOR_STORE_PATH / "documents.pkl"
INDEXED_FILE = VECTOR_STORE_PATH / "indexed_documents.json"


class VectorService:
    """FAISS vector database service with persistence."""

    def __init__(self, dimension: int = 384) -> None:
        self.dimension = dimension
        VECTOR_STORE_PATH.mkdir(exist_ok=True)
        self.index, self.documents = self._load()

    def _load(self):
        """Load index and documents from disk if they exist."""
        if INDEX_FILE.exists() and DOCUMENTS_FILE.exists():
            index = faiss.read_index(str(INDEX_FILE))
            with open(DOCUMENTS_FILE, "rb") as f:
                documents = pickle.load(f)
        else:
            index = faiss.IndexFlatL2(self.dimension)
            documents = []
        return index, documents

    def _save(self) -> None:
        """Persist index and documents to disk."""
        faiss.write_index(self.index, str(INDEX_FILE))
        with open(DOCUMENTS_FILE, "wb") as f:
            pickle.dump(self.documents, f)

    def load_indexed_documents(self) -> list[str]:
        """Load the list of already-indexed document names."""
        if INDEXED_FILE.exists():
            with open(INDEXED_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_indexed_documents(self, indexed: list[str]) -> None:
        """Persist the list of indexed document names."""
        with open(INDEXED_FILE, "w", encoding="utf-8") as f:
            json.dump(indexed, f, indent=2)

    def remove_document(self, chunks_to_remove: list[str]) -> int:
        """Rebuild the FAISS index excluding chunks belonging to the removed document."""
        chunks_to_remove_set = set(chunks_to_remove)
        remaining = [d for d in self.documents if d["chunk"] not in chunks_to_remove_set]
        removed_count = len(self.documents) - len(remaining)

        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []

        if remaining:
            texts = [d["chunk"] for d in remaining]
            from mcp_pdf.services.embedding_service import EmbeddingService
            embeddings = EmbeddingService().generate_embeddings(texts)
            embeddings = np.array(embeddings).astype("float32")
            self.index.add(embeddings)
            self.documents = remaining

        self._save()
        return removed_count

    def add_embeddings(
        self,
        embeddings,
        chunks: list[str],
    ) -> None:
        """Add embeddings and corresponding chunks, then save to disk."""
        embeddings = np.array(embeddings).astype("float32")
        self.index.add(embeddings)
        for chunk in chunks:
            self.documents.append({"chunk": chunk})
        self._save()

    def search(self, embedding, top_k: int = 3):
        """Perform semantic similarity search."""
        embedding = np.array([embedding]).astype("float32")
        distances, indices = self.index.search(embedding, top_k)

        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.documents):
                results.append(
                    {
                        "chunk": self.documents[idx]["chunk"],
                        "distance": float(distance),
                    }
                )
        return results