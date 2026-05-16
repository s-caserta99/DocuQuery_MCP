class DocumentNotFoundError(Exception):
    """Raised when a document cannot be found."""
    pass

class InvalidPDFError(Exception):
    """Raised when the PDF is invalid or corrupted."""
    pass

class NoteNotFoundError(Exception):
    """Raised when a note cannot be found."""
    pass