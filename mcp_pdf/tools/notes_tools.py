from datetime import datetime
from pathlib import Path

from fastmcp import FastMCP

from mcp_pdf.models.note import Note
from mcp_pdf.utils.errors import NoteNotFoundError

NOTES_DIR = Path("./notes")


def _note_path(title: str) -> Path:
    """Return the .txt file path for a note title."""
    safe_title = title.replace("/", "_").replace("\\", "_")
    return NOTES_DIR / f"{safe_title}.txt"


def _parse_note(path: Path) -> dict:
    """Parse a note .txt file into a dict."""
    lines = path.read_text(encoding="utf-8").splitlines()
    meta = {}
    content_lines = []
    in_content = False

    for line in lines:
        if line.startswith("title: "):
            meta["title"] = line[7:]
        elif line.startswith("document: "):
            meta["document"] = line[10:]
        elif line.startswith("created_at: "):
            meta["created_at"] = line[12:]
        elif line.startswith("updated_at: "):
            meta["updated_at"] = line[12:]
        elif line == "---":
            in_content = True
        elif in_content:
            content_lines.append(line)

    meta["content"] = "\n".join(content_lines)
    return meta


def _write_note(title: str, content: str, document: str, created_at: str, updated_at: str) -> None:
    """Write a note to a .txt file."""
    NOTES_DIR.mkdir(exist_ok=True)
    path = _note_path(title)
    text = (
        f"title: {title}\n"
        f"document: {document}\n"
        f"created_at: {created_at}\n"
        f"updated_at: {updated_at}\n"
        f"---\n"
        f"{content}"
    )
    path.write_text(text, encoding="utf-8")


def register_notes_tools(mcp: FastMCP) -> None:
    """Register note-taking MCP tools. Notes are saved as .txt files in the notes/ folder."""

    @mcp.tool()
    def create_note(title: str, content: str, document_name: str = "") -> dict:
        """Create a new note as a .txt file in the notes/ folder, optionally linked to a PDF document."""

        NOTES_DIR.mkdir(exist_ok=True)

        if _note_path(title).exists():
            raise ValueError(f"A note with title '{title}' already exists. Use update_note to modify it.")

        now = datetime.now().isoformat()
        _write_note(title, content, document_name, now, now)

        return {
            "message": f"Note '{title}' created successfully.",
            "file": str(_note_path(title)),
            "note": Note(
                title=title,
                content=content,
                document=document_name,
                created_at=now,
                updated_at=now,
                file=str(_note_path(title)),
            ).model_dump(),
        }

    @mcp.tool()
    def update_note(title: str, content: str) -> dict:
        """Update the content of an existing note."""

        path = _note_path(title)
        if not path.exists():
            raise NoteNotFoundError(f"Note '{title}' not found. Use create_note to create it first.")

        note = _parse_note(path)
        now = datetime.now().isoformat()
        _write_note(title, content, note.get("document", ""), note["created_at"], now)
        note["content"] = content
        note["updated_at"] = now

        return {"message": f"Note '{title}' updated successfully.", "note": note}

    @mcp.tool()
    def list_notes() -> list[dict]:
        """List all saved notes with their metadata."""

        NOTES_DIR.mkdir(exist_ok=True)
        notes = []

        for path in sorted(NOTES_DIR.glob("*.txt")):
            note = _parse_note(path)
            notes.append(Note(
                title=note.get("title", path.stem),
                document=note.get("document", ""),
                content=note.get("content", ""),
                created_at=note.get("created_at", ""),
                updated_at=note.get("updated_at", ""),
                file=str(path),
            ).model_dump())

        return notes

    @mcp.tool()
    def get_note(title: str) -> dict:
        """Retrieve the full content of a note by title."""

        path = _note_path(title)
        if not path.exists():
            raise NoteNotFoundError(f"Note '{title}' not found.")

        return _parse_note(path)

    @mcp.tool()
    def delete_note(title: str) -> dict:
        """Delete a note by title, removing its .txt file from the notes/ folder."""

        path = _note_path(title)
        if not path.exists():
            raise NoteNotFoundError(f"Note '{title}' not found.")

        path.unlink()

        return {"message": f"Note '{title}' deleted successfully.", "file_removed": str(path)}