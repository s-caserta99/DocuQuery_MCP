import json
from pathlib import Path

from fastmcp import FastMCP

from mcp_pdf.services.pdf_service import PDFService
from mcp_pdf.utils.errors import DocumentNotFoundError

pdf_service = PDFService()

NOTES_DIR = Path("./notes")
VECTOR_STORE_PATH = Path("./vector_store")
INDEXED_FILE = VECTOR_STORE_PATH / "indexed_documents.json"


def register_resources(mcp: FastMCP) -> None:
    """Register MCP resources for documents, notes, and vector store."""


    @mcp.resource("documents://list")
    def list_documents_resource() -> str:
        """Return a list of all available PDF documents."""
        documents = pdf_service.list_documents()
        if not documents:
            return "No PDF documents found."
        return "\n".join(documents)

    @mcp.resource("documents://{document_name}")
    def document_content_resource(document_name: str) -> str:
        """Return the full text content of a PDF document exactly as-is, without translating or modifying it."""
        try:
            return pdf_service.extract_text(document_name)
        except FileNotFoundError:
            raise DocumentNotFoundError(f"Document '{document_name}' not found.")

    @mcp.resource("documents://metadata/{document_name}")
    def document_metadata_resource(document_name: str) -> str:
        """Return metadata for a PDF document (title, author, pages, subject)."""
        try:
            metadata = pdf_service.get_metadata(document_name)
            return metadata.model_dump_json(indent=2)
        except FileNotFoundError:
            raise DocumentNotFoundError(f"Document '{document_name}' not found.")


    @mcp.resource("notes://list")
    def list_notes_resource() -> str:
        """Return a list of all saved notes from the notes/ folder."""
        NOTES_DIR.mkdir(exist_ok=True)
        notes = sorted(NOTES_DIR.glob("*.txt"))
        if not notes:
            return "No notes found."
        return "\n".join(p.stem for p in notes)

    @mcp.resource("notes://{title}")
    def note_content_resource(title: str) -> str:
        """Return the full content of a note by title."""
        safe_title = title.replace("/", "_").replace("\\", "_")
        path = NOTES_DIR / f"{safe_title}.txt"
        if not path.exists():
            return f"Note '{title}' not found."
        return path.read_text(encoding="utf-8")


    @mcp.resource("index://status")
    def index_status_resource() -> str:
        """Return the list of documents currently indexed for semantic search."""
        if not INDEXED_FILE.exists():
            return json.dumps({"indexed_documents": [], "total": 0}, indent=2)
        with open(INDEXED_FILE, "r", encoding="utf-8") as f:
            indexed = json.load(f)
        return json.dumps({"indexed_documents": indexed, "total": len(indexed)}, indent=2)