import uvicorn

from mcp_pdf.config.settings import settings
from mcp_pdf.server import mcp, BearerAuthMiddleware


def main() -> None:
    """Run the MCP server over HTTP (streamable-http transport)."""
    app = mcp.http_app(path="/mcp")
    app.add_middleware(BearerAuthMiddleware)

    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()