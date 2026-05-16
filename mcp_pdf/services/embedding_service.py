from sentence_transformers import SentenceTransformer
from mcp_pdf.config.settings import settings

class EmbeddingService:
    """Service responsible for generating text embeddings."""

    def __init__(self) -> None:
        self.model = SentenceTransformer(settings.embedding_model)

    def generate_embedding(self, text: str):
        """Generate embedding for a single text."""
        return self.model.encode(text)

    def generate_embeddings(self, texts: list[str]):
        """Generate embeddings for multiple texts."""
        return self.model.encode(texts)