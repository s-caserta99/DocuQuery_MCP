class SummaryService:
    """Basic summarization service."""

    def summarize(
        self,
        text: str,
        max_length: int = 1500,
    ) -> str:
        """Generate a simple extractive summary."""
        cleaned_text = text.strip()
        
        if len(cleaned_text) <= max_length:
            return cleaned_text
            
        return cleaned_text[:max_length] + "..."