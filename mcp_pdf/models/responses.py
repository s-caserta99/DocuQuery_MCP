from pydantic import BaseModel, Field


class SummaryResponse(BaseModel):
    """Document summarization response."""

    document: str = Field(..., description="Document filename")
    summary: str = Field(..., description="Generated summary")
    summary_length: int = Field(..., ge=0, description="Summary character count")


class ServerStatusResponse(BaseModel):
    """Server status response."""

    status: str = Field(..., description="Server status")
    service: str = Field(..., description="Service name")
    timestamp: str = Field(..., description="Current timestamp")


class ErrorResponse(BaseModel):
    """Generic error response."""

    error: str = Field(..., description="Error message")
    details: str | None = Field(default=None, description="Additional error details")
