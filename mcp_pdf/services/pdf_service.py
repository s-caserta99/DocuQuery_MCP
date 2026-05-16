from pathlib import Path
import fitz  # PyMuPDF

from mcp_pdf.config.settings import settings
from mcp_pdf.models.document import DocumentMetadata
from mcp_pdf.utils.errors import DocumentNotFoundError, InvalidPDFError


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
            raise DocumentNotFoundError(
                f"Document '{document_name}' not found."
            )

        return document_path

    def extract_text(self, document_name: str) -> str:
        """Extracts all text content from a PDF document."""
        document_path = self.get_document_path(document_name)

        try:
            with fitz.open(document_path) as pdf_document:
                return "".join(page.get_text() for page in pdf_document)
        except fitz.FileDataError as e:
            raise InvalidPDFError(
                f"Document '{document_name}' is corrupted or not a valid PDF: {e}"
            )

    def get_metadata(self, document_name: str) -> DocumentMetadata:
        """Extracts basic metadata from the PDF."""
        document_path = self.get_document_path(document_name)

        try:
            with fitz.open(document_path) as pdf_document:
                meta = pdf_document.metadata
                return DocumentMetadata(
                    filename=document_name,
                    pages=len(pdf_document),
                    title=meta.get("title") or None,
                    author=meta.get("author") or None,
                    subject=meta.get("subject") or None,
                )
        except fitz.FileDataError as e:
            raise InvalidPDFError(
                f"Document '{document_name}' is corrupted or not a valid PDF: {e}"
            )