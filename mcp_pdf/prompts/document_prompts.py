from fastmcp import FastMCP

def register_prompts(mcp: FastMCP) -> None:
    """Register reusable MCP prompts."""

    @mcp.prompt()
    def summarize_research_paper(document_name: str) -> str:
        """Prompt for summarizing academic papers."""
        return f"""
        Analyze the research paper '{document_name}'.
        Your summary should include:
        - Main topic
        - Research objective
        - Methodology
        - Key findings
        - Final conclusions
        Keep the response concise and academically structured.
        """

    @mcp.prompt()
    def extract_key_findings(document_name: str) -> str:
        """Prompt for extracting key findings."""
        return f"""
        Read the document '{document_name}' and extract:
        - Important discoveries
        - Significant results
        - Technical insights
        - Recommendations
        Return the findings as bullet points.
        """

    @mcp.prompt()
    def compare_documents(document_a: str, document_b: str) -> str:
        """Prompt for comparing two documents."""
        return f"""
        Compare the following documents:
        - {document_a}
        - {document_b}
        Focus on:
        - Similarities
        - Differences
        - Common themes
        - Contrasting methodologies
        - Final conclusions
        """

    @mcp.prompt()
    def generate_study_notes(document_name: str) -> str:
        """Prompt for generating study notes."""
        return f"""
        Generate clear study notes from '{document_name}'.
        Organize the notes into:
        - Definitions
        - Main concepts
        - Important formulas
        - Examples
        - Summary
        """