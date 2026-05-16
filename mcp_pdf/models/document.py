from datetime import datetime, timezone
from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    """Metadata extracted from a PDF document."""

    filename: str = Field(..., description="PDF filename")

    pages: int = Field(
        ...,
        gt=0,
        description="Number of pages",
    )

    title: str | None = Field(
        default=None,
        description="Document title",
    )

    author: str | None = Field(
        default=None,
        description="Document author",
    )

    subject: str | None = Field(
        default=None,
        description="Document subject",
    )

    indexed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Index timestamp",
    )
