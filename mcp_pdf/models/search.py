from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    """Keyword search result."""

    page: int = Field(..., ge=1)

    match: str = Field(
        ...,
        description="Matched query string",
    )

    text: str = Field(
        ...,
        description="Relevant text snippet",
    )


class SemanticSearchResult(BaseModel):
    """Semantic search result."""

    chunk: str = Field(
        ...,
        description="Relevant document chunk",
    )

    distance: float = Field(
        ...,
        description="Vector similarity distance",
    )