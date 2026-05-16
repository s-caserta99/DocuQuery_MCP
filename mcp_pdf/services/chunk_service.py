class ChunkService:
    """Service to split text into overlapping chunks for embedding."""

    def chunk_text(self, text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
        """Split text into chunks of chunk_size with overlap between consecutive chunks."""
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            if chunk.strip():  
                chunks.append(chunk)
            start += chunk_size - overlap
        return chunks