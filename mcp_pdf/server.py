from contextlib import asynccontextmanager

from fastmcp import FastMCP

from mcp_pdf.config.settings import settings
from mcp_pdf.prompts.document_prompts import register_prompts
from mcp_pdf.resources.document_resources import register_resources
from mcp_pdf.tools.admin_tools import register_admin_tools
from mcp_pdf.tools.notes_tools import register_notes_tools
from mcp_pdf.tools.pdf_tools import register_pdf_tools
from mcp_pdf.tools.search_tools import register_search_tools
from mcp_pdf.tools.summary_tools import register_summary_tools
from mcp_pdf.utils.helpers import ensure_required_directories
from mcp_pdf.utils.logger import logger


@asynccontextmanager
async def lifespan(_: FastMCP):
    """Application lifecycle management."""
    ensure_required_directories()
    logger.info(
        "Starting MCP PDF Assistant on http://localhost:%s/mcp/", settings.port
    )
    yield
    logger.info("Shutting down MCP PDF Assistant...")


mcp = FastMCP(
    name="DocuQuery MCP",
    instructions="MCP server for PDF analysis and semantic document search.",
    lifespan=lifespan,
)


register_admin_tools(mcp)
register_pdf_tools(mcp)
register_search_tools(mcp)
register_summary_tools(mcp)
register_notes_tools(mcp)
register_resources(mcp)
register_prompts(mcp)