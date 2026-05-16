from fastmcp import FastMCP

from mcp_pdf.models.responses import SummaryResponse
from mcp_pdf.services.pdf_service import PDFService
from mcp_pdf.services.summary_service import SummaryService

_pdf_service = PDFService()
_summary_service = SummaryService()


def register_summary_tools(mcp: FastMCP) -> None:
    """Register summarization tools."""

    @mcp.tool()
    def summarize_document(document_name: str, max_length: int = 1500) -> SummaryResponse:
        """Generate a simple summary from the PDF content."""
        full_text = _pdf_service.extract_text(document_name)
        summary = _summary_service.summarize(full_text, max_length=max_length)

        return SummaryResponse(
            document=document_name,
            summary=summary,
            summary_length=len(summary),
        )