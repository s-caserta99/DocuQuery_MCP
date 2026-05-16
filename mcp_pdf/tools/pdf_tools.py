from fastmcp import FastMCP
from pathlib import Path

from mcp_pdf.config.settings import settings
from mcp_pdf.services.pdf_service import PDFService
from mcp_pdf.utils.errors import DocumentNotFoundError

_pdf_service = PDFService()


def register_pdf_tools(mcp: FastMCP) -> None:
    """Register PDF-related MCP tools."""

    @mcp.tool()
    def list_documents() -> list[str]:
        """List all available PDF documents."""
        return _pdf_service.list_documents()

    @mcp.tool()
    def extract_text(document_name: str) -> str:
        """Extract full text from a PDF document. Return the extracted text exactly as-is, without translating, summarizing, or modifying it in any way."""
        return _pdf_service.extract_text(document_name)

    @mcp.tool()
    def get_document_metadata(document_name: str) -> dict:
        """Return PDF metadata."""
        return _pdf_service.get_metadata(document_name).model_dump()

    @mcp.tool()
    def extract_images(document_name: str) -> list[dict]:
        """Extract all images from a PDF document and save them to the images/ folder."""
        import fitz

        document_path = _pdf_service.get_document_path(document_name)
        images_dir = Path("./images")
        images_dir.mkdir(exist_ok=True)

        extracted = []

        with fitz.open(document_path) as pdf_document:
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

        return extracted

    @mcp.tool()
    def delete_document_images(document_name: str) -> dict:
        """Delete all extracted images belonging to a specific PDF document from the images/ folder."""
        images_dir = Path("./images")

        if not images_dir.exists():
            return {"message": "No images folder found.", "deleted": []}

        deleted = [
            image_path.name
            for image_path in images_dir.glob(f"{document_name}_*")
            if not image_path.unlink()  # unlink() returns None, so always truthy after deletion
        ]

        if not deleted:
            return {"message": f"No images found for '{document_name}'.", "deleted": []}

        return {
            "message": f"Deleted {len(deleted)} image(s) for '{document_name}'.",
            "deleted": deleted,
        }