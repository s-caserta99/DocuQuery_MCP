from datetime import datetime
 
from fastmcp import FastMCP
 
from mcp_pdf.models.responses import ServerStatusResponse
 
 
def register_admin_tools(mcp: FastMCP) -> None:
    """Register admin/debug tools."""
 
    @mcp.tool()
    def server_status() -> ServerStatusResponse:
        """Return current server status."""
 
        return ServerStatusResponse(
            status="running",
            timestamp=datetime.now().isoformat(),
            service="DocuQuery MCP",
        )
 