from pathlib import Path
import json
import urllib.request
 
import fitz
from fastmcp import FastMCP
 
from mcp_pdf.config.settings import settings
from mcp_pdf.models.document import DocumentMetadata
from mcp_pdf.utils.errors import DocumentNotFoundError, InvalidPDFError
 

def register_pdf_tools(mcp: FastMCP) -> None:
    """Register PDF-related MCP tools."""
 
    @mcp.tool()
    def list_documents() -> list[str]:
        """List all available PDF documents."""
 
        documents_path = Path(settings.documents_path)
 
        pdf_files = [
            file.name
            for file in documents_path.glob("*.pdf")
        ]
 
        return pdf_files
 
    @mcp.tool()
    def extract_text(document_name: str) -> str:
        """Extract full text from a PDF document. Return the extracted text exactly as-is, without translating, summarizing, or modifying it in any way."""
 
        document_path = Path(settings.documents_path) / document_name
 
        if not document_path.exists():
            raise DocumentNotFoundError(
                f"Document '{document_name}' not found."
            )
 
        try:
            pdf_document = fitz.open(document_path)
        except Exception as e:
            raise InvalidPDFError(f"Document '{document_name}' is corrupted: {e}")
 
        text = ""
 
        for page in pdf_document:
            text += page.get_text()
 
        pdf_document.close()
 
        return text
 
    @mcp.tool()
    def extract_images(document_name: str) -> list[dict]:
        """Extract all images from a PDF document and save them to the images/ folder."""
 
        document_path = Path(settings.documents_path) / document_name
 
        if not document_path.exists():
            raise DocumentNotFoundError(
                f"Document '{document_name}' not found."
            )
 
        images_dir = Path("./images")
        images_dir.mkdir(exist_ok=True)
 
        try:
            pdf_document = fitz.open(document_path)
        except Exception as e:
            raise InvalidPDFError(f"Document '{document_name}' is corrupted: {e}")
        extracted = []
 
        for page_number, page in enumerate(pdf_document):
            for img_index, img in enumerate(page.get_images(full=True)):
                xref = img[0]
                base_image = pdf_document.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
 
                image_filename = f"{document_name}_p{page_number + 1}_img{img_index + 1}.{image_ext}"
                image_path = images_dir / image_filename
 
                with open(image_path, "wb") as f:
                    f.write(image_bytes)
 
                extracted.append({
                    "filename": image_filename,
                    "page": page_number + 1,
                    "width": base_image["width"],
                    "height": base_image["height"],
                    "format": image_ext,
                    "saved_to": str(image_path),
                })
 
        pdf_document.close()
 
        return extracted
 
    @mcp.tool()
    def delete_document_images(document_name: str) -> dict:
        """Delete all extracted images belonging to a specific PDF document from the images/ folder."""
 
        images_dir = Path("./images")
 
        if not images_dir.exists():
            return {"message": "No images folder found.", "deleted": []}
 
        deleted = []
        for image_path in images_dir.glob(f"{document_name}_*"):
            image_path.unlink()
            deleted.append(image_path.name)
 
        if not deleted:
            return {"message": f"No images found for '{document_name}'.", "deleted": []}
 
        return {
            "message": f"Deleted {len(deleted)} image(s) for '{document_name}'.",
            "deleted": deleted,
        }
 
    @mcp.tool()
    def get_document_metadata(document_name: str) -> DocumentMetadata:
        """Return PDF metadata."""
 
        document_path = Path(settings.documents_path) / document_name
 
        if not document_path.exists():
            raise DocumentNotFoundError(
                f"Document '{document_name}' not found."
            )
 
        try:
            pdf_document = fitz.open(document_path)
        except Exception as e:
            raise InvalidPDFError(f"Document '{document_name}' is corrupted or not a valid PDF: {e}")
 
        metadata = DocumentMetadata(
            filename=document_name,
            pages=len(pdf_document),
            title=pdf_document.metadata.get("title"),
            author=pdf_document.metadata.get("author"),
            subject=pdf_document.metadata.get("subject"),
        )
 
        pdf_document.close()
 
        return metadata
 