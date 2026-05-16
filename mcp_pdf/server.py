from contextlib import asynccontextmanager

from fastmcp import FastMCP
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

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


class BearerAuthMiddleware(BaseHTTPMiddleware):
    """Reject requests that don't carry a valid Bearer token."""

    async def dispatch(self, request: Request, call_next):
        if request.url.path in ("/health", "/"):
            return await call_next(request)

        if not settings.mcp_auth_token:
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                {"error": "Missing or malformed Authorization header."},
                status_code=401,
            )

        token = auth_header.removeprefix("Bearer ").strip()
        if token != settings.mcp_auth_token:
            return JSONResponse(
                {"error": "Invalid token."},
                status_code=403,
            )

        return await call_next(request)


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