from pathlib import Path

import fitz
from fastmcp import FastMCP

from mcp_pdf.config.settings import settings
from mcp_pdf.models.responses import SummaryResponse
from mcp_pdf.services.summary_service import SummaryService
from mcp_pdf.utils.errors import DocumentNotFoundError, InvalidPDFError

_summary_service = SummaryService()


def register_summary_tools(mcp: FastMCP) -> None:
    """Register summarization tools."""

    @mcp.tool()
    def summarize_document(document_name: str, max_length: int = 1500) -> SummaryResponse:
        """Generate a simple summary from the PDF content."""

        document_path = Path(settings.documents_path) / document_name

        if not document_path.exists():
            raise DocumentNotFoundError(
                f"Document '{document_name}' not found."
            )

        try:
            pdf_document = fitz.open(document_path)
        except Exception as e:
            raise InvalidPDFError(f"Document '{document_name}' is corrupted or not a valid PDF: {e}")

        full_text = ""
        for page in pdf_document:
            full_text += page.get_text()
        pdf_document.close()

        summary = _summary_service.summarize(full_text, max_length=max_length)

        return SummaryResponse(
            document=document_name,
            summary=summary,
            summary_length=len(summary),
        )