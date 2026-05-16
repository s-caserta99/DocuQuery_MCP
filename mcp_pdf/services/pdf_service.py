from pathlib import Path
import fitz  # PyMuPDF

from mcp_pdf.config.settings import settings
from mcp_pdf.models.document import DocumentMetadata


class PDFService:
    """Service responsible for PDF operations."""

    def __init__(self) -> None:
        self.documents_path = Path(settings.documents_path)

    def list_documents(self) -> list[str]:
        """Returns a list of all PDF filenames in the configured directory."""
        return [file.name for file in self.documents_path.glob("*.pdf")]

    def get_document_path(self, document_name: str) -> Path:
        """Constructs and validates the path for a specific document."""
        document_path = self.documents_path / document_name

        if not document_path.exists():
            raise FileNotFoundError(
                f"Document '{document_name}' not found."
            )

        return document_path

    def extract_text(self, document_name: str) -> str:
        """Extracts all text content from a PDF document."""
        document_path = self.get_document_path(document_name)
        text = ""
        
        # Apertura del documento con PyMuPDF
        with fitz.open(document_path) as pdf_document:
            for page in pdf_document:
                text += page.get_text()
                
        return text

    def get_metadata(self, document_name: str) -> DocumentMetadata:
        """Extracts basic metadata from the PDF."""
        document_path = self.get_document_path(document_name)
        
        with fitz.open(document_path) as pdf_document:
            meta = pdf_document.metadata
            return DocumentMetadata(
                filename=document_name,
                title=meta.get("title", ""),
                author=meta.get("author", ""),
                pages=len(pdf_document)
            )