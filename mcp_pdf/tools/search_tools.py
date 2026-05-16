import asyncio
from pathlib import Path

import fitz
from fastmcp import FastMCP

from mcp_pdf.config.settings import settings
from mcp_pdf.models.search import SearchResult, SemanticSearchResult
from mcp_pdf.services.chunk_service import ChunkService
from mcp_pdf.services.embedding_service import EmbeddingService
from mcp_pdf.services.vector_service import VectorService
from mcp_pdf.utils.errors import DocumentNotFoundError, InvalidPDFError

_vector_service = VectorService(dimension=384)
_embedding_service = EmbeddingService()
_chunk_service = ChunkService()
_indexed_documents: list[str] = _vector_service.load_indexed_documents()


def register_search_tools(mcp: FastMCP) -> None:
    """Register search-related tools."""

    @mcp.tool()
    async def search_document(document_name: str, query: str) -> list[SearchResult]:
        """Search for text occurrences inside a PDF document."""

        document_path = Path(settings.documents_path) / document_name

        if not document_path.exists():
            raise DocumentNotFoundError(
                f"Document '{document_name}' not found."
            )

        try:
            pdf_document = fitz.open(document_path)
        except Exception as e:
            raise InvalidPDFError(f"Document '{document_name}' is corrupted or not a valid PDF: {e}")

        def _search() -> list[SearchResult]:
            results = []
            for page_number, page in enumerate(pdf_document):
                page_text = page.get_text()
                if query.lower() in page_text.lower():
                    results.append(
                        SearchResult(
                            page=page_number + 1,
                            match=query,
                            text=page_text[:1000],
                        )
                    )
            pdf_document.close()
            return results

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, _search)

    @mcp.tool()
    async def index_document(document_name: str) -> dict:
        """Index a PDF document for semantic search using embeddings and FAISS."""

        document_path = Path(settings.documents_path) / document_name

        if not document_path.exists():
            raise DocumentNotFoundError(
                f"Document '{document_name}' not found."
            )

        if document_name in _indexed_documents:
            return {
                "message": f"Document '{document_name}' is already indexed.",
                "indexed_documents": _indexed_documents,
            }

        try:
            pdf_document = fitz.open(document_path)
        except Exception as e:
            raise InvalidPDFError(f"Document '{document_name}' is corrupted or not a valid PDF: {e}")

        def _extract_and_chunk() -> list[str]:
            full_text = ""
            for page in pdf_document:
                full_text += page.get_text()
            pdf_document.close()
            return _chunk_service.chunk_text(
                full_text,
                chunk_size=settings.max_chunk_size,
                overlap=settings.chunk_overlap,
            )

        loop = asyncio.get_event_loop()
        chunks = await loop.run_in_executor(None, _extract_and_chunk)

        embeddings = await loop.run_in_executor(
            None,
            _embedding_service.generate_embeddings,
            chunks,
        )

        _vector_service.add_embeddings(embeddings, chunks)
        _indexed_documents.append(document_name)
        _vector_service.save_indexed_documents(_indexed_documents)

        return {
            "message": f"Document '{document_name}' indexed successfully.",
            "chunks_created": len(chunks),
            "indexed_documents": _indexed_documents,
        }

    @mcp.tool()
    async def semantic_search(query: str, top_k: int = 3) -> dict:
        """Search indexed documents semantically using embeddings and FAISS."""

        if not _indexed_documents:
            return {
                "query": query,
                "error": "No documents indexed yet. Use index_document first.",
                "indexed_documents": [],
            }

        loop = asyncio.get_event_loop()
        query_embedding = await loop.run_in_executor(
            None,
            _embedding_service.generate_embedding,
            query,
        )

        raw_results = _vector_service.search(query_embedding, top_k=top_k)

        results = [
            SemanticSearchResult(
                chunk=r["chunk"],
                distance=r["distance"],
            )
            for r in raw_results
        ]

        return {
            "query": query,
            "indexed_documents": _indexed_documents,
            "results": [r.model_dump() for r in results],
        }

    @mcp.tool()
    async def remove_document_index(document_name: str) -> dict:
        """Remove a document from the semantic search index."""

        if document_name not in _indexed_documents:
            raise ValueError(
                f"Document '{document_name}' is not indexed."
            )

        document_path = Path(settings.documents_path) / document_name

        if document_path.exists():
            try:
                pdf_document = fitz.open(document_path)
            except Exception as e:
                raise InvalidPDFError(f"Document '{document_name}' is corrupted or not a valid PDF: {e}")

            def _extract_and_rebuild() -> int:
                full_text = ""
                for page in pdf_document:
                    full_text += page.get_text()
                pdf_document.close()
                chunks = _chunk_service.chunk_text(
                    full_text,
                    chunk_size=settings.max_chunk_size,
                    overlap=settings.chunk_overlap,
                )
                return _vector_service.remove_document(chunks)

            loop = asyncio.get_event_loop()
            removed_count = await loop.run_in_executor(None, _extract_and_rebuild)
        else:
            removed_count = _vector_service.remove_document([])

        _indexed_documents.remove(document_name)
        _vector_service.save_indexed_documents(_indexed_documents)

        return {
            "message": f"Document '{document_name}' removed from index.",
            "chunks_removed": removed_count,
            "indexed_documents": _indexed_documents,
        }

    @mcp.tool()
    def list_indexed_documents() -> dict:
        """List all documents currently indexed for semantic search."""

        return {
            "indexed_documents": _indexed_documents,
            "total": len(_indexed_documents),
        }