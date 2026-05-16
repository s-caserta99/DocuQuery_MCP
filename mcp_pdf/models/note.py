from pydantic import BaseModel, Field


class Note(BaseModel):
    """A text note optionally linked to a PDF document."""

    title: str = Field(..., description="Note title")
    content: str = Field(..., description="Note content")
    document: str = Field(default="", description="Linked PDF document name")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    file: str = Field(default="", description="Path to the .txt file")