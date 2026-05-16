# DocuQuery MCP 

> An MCP (Model Context Protocol) server that transforms how researchers, PhD students, and academics interact with scientific literature. Instead of manually reading through papers, DocuQuery MCP lets you ask questions, extract information, and build knowledge directly from your PDF documents through any AI agent that supports the MCP protocol.

---

## What is this project?

DocuQuery MCP is a local server that exposes a set of tools, resources, and prompts over the [Model Context Protocol](https://modelcontextprotocol.io). Once running, any compatible AI agent (such as Google Gemini via Antigravity, Claude via Claude Code, or any other MCP-compatible client) can use these capabilities to interact with your PDF library.

### Who is it for?

- **Students** writing their thesis and needing to quickly extract key concepts from dozens of papers
- **PhD researchers** conducting systematic literature reviews
- **Academics** comparing methodologies across multiple studies
- **Anyone** who works regularly with scientific PDFs and wants AI-assisted reading

### What can it do?

- Extract and search text from PDFs
- Extract images embedded in documents
- Generate document summaries
- Perform **semantic search** across indexed documents using embeddings and FAISS — finding relevant passages even when exact keywords don't match
- Extract authors from scientific papers using AI
- Create, update, and manage research notes linked to specific documents
- Expose documents and notes as MCP resources for direct agent access

---

## Repository Structure

```
mcp-pdf/
├── mcp_pdf/
│   ├── server.py                  # Entry point — registers all tools, resources, prompts
│   ├── __main__.py                # Allows running with: uv run mcp-server
│   ├── config/
│   │   └── settings.py            # All configuration loaded from .env
│   ├── tools/                     # MCP tools (callable actions)
│   │   ├── admin_tools.py         # server_status
│   │   ├── pdf_tools.py           # list_documents, extract_text, extract_images,
│   │   │                          # delete_document_images, get_document_metadata,
│   │   │                          # extract_authors
│   │   ├── search_tools.py        # search_document, index_document, semantic_search,
│   │   │                          # remove_document_index, list_indexed_documents
│   │   ├── summary_tools.py       # summarize_document
│   │   └── notes_tools.py         # create_note, update_note, list_notes,
│   │                              # get_note, delete_note
│   ├── resources/
│   │   └── document_resources.py  # MCP resources: documents://, notes://, index://
│   ├── prompts/
│   │   └── document_prompts.py    # MCP prompts for academic use cases
│   ├── services/                  # Business logic (used by tools)
│   │   ├── pdf_service.py         # PDF reading (used by resources)
│   │   ├── summary_service.py     # Text truncation/summarization logic
│   │   ├── chunk_service.py       # Splits text into overlapping chunks
│   │   ├── embedding_service.py   # Generates vector embeddings (all-MiniLM-L6-v2)
│   │   └── vector_service.py      # FAISS index management with disk persistence
│   ├── models/                    # Pydantic data models
│   │   ├── document.py            # DocumentMetadata
│   │   ├── note.py                # Note
│   │   ├── responses.py           # SummaryResponse, ServerStatusResponse, ErrorResponse
│   │   └── search.py              # SearchResult, SemanticSearchResult
│   ├── utils/
│   │   ├── errors.py              # DocumentNotFoundError, InvalidPDFError, NoteNotFoundError
│   │   ├── helpers.py             # ensure_required_directories() — auto-creates folders
│   │   └── logger.py              # Centralized logging configuration
│   └── storage/
│       ├── repository.py          # Abstract DocumentRepository interface
│       └── sqlite_repository.py   # SQLite implementation (reserved for future use)
├── documents/                     # Place your PDF files here
├── images/                        # Extracted images are saved here (auto-created)
├── notes/                         # Research notes saved as .txt files (auto-created)
├── vector_store/                  # FAISS index persisted here (auto-created)
│   ├── faiss.index
│   ├── documents.pkl
│   └── indexed_documents.json
├── pyproject.toml                 # Project dependencies managed by uv
├── .env.example                   # Environment variable template
└── README.md                      # This file
```

---

## Setup and Installation

Follow these steps carefully to configure and run the server.

### Step 1 — Clone or download the repository

```bash
git clone <repository-url> 
```

### Step 2 — Install dependencies

```bash
uv sync
```

This reads `pyproject.toml` and installs all required packages into an isolated virtual environment. The key dependencies are:

| Package | Purpose |
|---|---|
| `fastmcp` | MCP server framework |
| `pymupdf` | PDF reading and image extraction |
| `sentence-transformers` | Generates text embeddings for semantic search |
| `faiss-cpu` | Vector similarity search index |
| `pydantic` | Data validation and serialization |
| `pydantic-settings` | Environment variable management |

### Step 3 — Configure the environment

Copy the example environment file:

```bash
cp .env.example .env
```

Open `.env` in any text editor. The default values work out of the box for local use:

```env
APP_NAME=DocuQuery MCP
DEBUG=true

DOCUMENTS_PATH=./documents
VECTOR_STORE_PATH=./vector_store

EMBEDDING_MODEL=all-MiniLM-L6-v2
MAX_CHUNK_SIZE=800
CHUNK_OVERLAP=100

HOST=0.0.0.0
PORT=8001
LOG_LEVEL=INFO

# Optional: set a Bearer token to protect the server
# Generate one with: python3 -c "import secrets; print(secrets.token_hex(32))"
MCP_AUTH_TOKEN=
```

If you set `MCP_AUTH_TOKEN`, every request must include the header:
```
Authorization: Bearer <your-token>
```

### Step 4 — Add your PDF documents

Place your PDF files inside the `documents/` folder:

```bash
cp /path/to/your/paper.pdf documents/
```

The `documents/` folder is created automatically on first server startup if it does not exist.

### Step 5 — Start the server

```bash
uv run mcp-server
```

You should see output like:

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
2026-05-03 10:00:00,000 - INFO - Starting MCP PDF Assistant on http://localhost:8001/mcp/
2026-05-03 10:00:00,000 - WARNING - Authentication disabled — set MCP_AUTH_TOKEN in .env to enable.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

The server is now running at `http://localhost:8001/mcp`.

To stop the server press `CTRL+C`.

### Step 6 — Verify the server is running

Open a second terminal and run:

```bash
curl -s -X POST http://localhost:8001/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"0.1"}}}' \
  | grep "^data:" | sed 's/^data: //'
```

You should receive a JSON response containing `"name": "DocuQuery MCP"`.

---

## Connecting to Antigravity

Antigravity is a VS Code-based AI coding environment. To connect DocuQuery MCP to its Agent panel:

### Step 1 — Open the MCP configuration file

In the Antigravity Agent panel, click the **⋯** menu → **MCP Servers** → **Edit configuration**.

### Step 2 — Add the server configuration

Paste the following into the configuration file:

```json
{
  "mcpServers": {
    "mcp-pdf": {
      "serverUrl": "http://localhost:8001/mcp",
      "disabledTools": []
    }
  }
}
```

If you set an `MCP_AUTH_TOKEN`, add the Authorization header:

```json
{
  "mcpServers": {
    "mcp-pdf": {
      "serverUrl": "http://localhost:8001/mcp",
      "headers": {
        "Authorization": "Bearer <your-token>"
      },
      "disabledTools": []
    }
  }
}
```

### Step 3 — Reload and verify

Save the file and reload the Antigravity window (`Cmd+Shift+P` → `Developer: Reload Window`). Make sure the MCP server is running in a terminal. In the Agent panel, open **Manage MCP Servers** — you should see `mcp-pdf` listed with all tools enabled (16/16 tools with blue toggles).

---

## Available Tools

### Admin

| Tool | Description | Parameters |
|---|---|---|
| `server_status` | Returns current server status and timestamp | none |

### PDF Management

| Tool | Description | Parameters |
|---|---|---|
| `list_documents` | Lists all PDF files in the `documents/` folder | none |
| `extract_text` | Extracts the full raw text from a PDF | `document_name` |
| `extract_images` | Extracts all images and saves them to `images/` | `document_name` |
| `delete_document_images` | Deletes extracted images for a specific document | `document_name` |
| `get_document_metadata` | Returns title, author, pages, subject | `document_name` |
| `extract_authors` | Uses AI to identify authors and affiliations from first pages | `document_name` |
| `summarize_document` | Generates a text summary of the document content | `document_name`, `max_length` (default: 1500) |

### Search

| Tool | Description | Parameters |
|---|---|---|
| `search_document` | Keyword search — finds exact text occurrences by page | `document_name`, `query` |
| `index_document` | Indexes a document for semantic search (generates embeddings) | `document_name` |
| `semantic_search` | Finds relevant passages by meaning, not just keywords | `query`, `top_k` (default: 3) |
| `remove_document_index` | Removes a document from the FAISS index | `document_name` |
| `list_indexed_documents` | Lists all currently indexed documents | none |

### Notes

| Tool | Description | Parameters |
|---|---|---|
| `create_note` | Creates a new `.txt` note in `notes/`, optionally linked to a PDF | `title`, `content`, `document_name` |
| `update_note` | Updates the content of an existing note | `title`, `content` |
| `get_note` | Retrieves the full content of a note | `title` |
| `list_notes` | Lists all saved notes with metadata | none |
| `delete_note` | Deletes a note and its `.txt` file | `title` |

---

## Available Resources

MCP Resources expose data that agents can read directly via URI, without invoking a tool action.

| URI | Description |
|---|---|
| `documents://list` | Plain-text list of all available PDFs |
| `documents://{document_name}` | Full raw text of a specific PDF |
| `documents://metadata/{document_name}` | JSON metadata for a specific PDF |
| `notes://list` | List of all note titles |
| `notes://{title}` | Full content of a specific note |
| `index://status` | JSON list of documents currently in the FAISS index |

---

## Available Prompts

MCP Prompts are reusable instruction templates that guide the agent through structured academic tasks. Invoke them by name in the Agent panel.

| Prompt | Description | Parameters |
|---|---|---|
| `summarize_research_paper` | Structured academic summary: topic, objective, methodology, findings, conclusions | `document_name` |
| `extract_key_findings` | Extracts key discoveries, results, and recommendations as bullet points | `document_name` |
| `compare_documents` | Side-by-side comparison of two papers: similarities, differences, methodologies | `document_a`, `document_b` |
| `generate_study_notes` | Organizes content into definitions, concepts, formulas, examples, summary | `document_name` |

---

## Example Documents

This repository includes a set of example scientific papers on **deep learning for intracranial vessel segmentation** to demonstrate the server's capabilities across real academic content.

---

## Testing the Server — Example Queries

The following queries can be typed directly into the Antigravity Agent panel to verify that all features work correctly.

### Server and document management

```
What is the current server status?
```
```
List all available documents
```
```
Show me the metadata of nins-13-00097.pdf
```
```
Extract the text from nins-13-00097.pdf without translating or modifying it
```
```
Extract all images from nins-13-00097.pdf
```
```
Extract the authors from nins-13-00097.pdf
```

### Search

```
Search for the word "segmentation" in nins-13-00097.pdf
```
```
Index all available documents
```
```
List the documents that have been indexed
```
```
Which document discusses a study where a neural network is used for vessel segmentation?
```
```
Search semantically for "deep learning architecture for intracranial artery segmentation"
```

### Notes workflow

```
Extract the abstract from nins-13-00097.pdf and create a note titled "Abstract nins" with that content, linked to nins-13-00097.pdf
```
```
List all saved notes
```
```
Show me the note "Abstract nins"
```
```
Summarize the document nins-13-00097.pdf, then update the note "Abstract nins" by adding a new paragraph titled "Summary" with the document summary
```
```
Show me the updated note "Abstract nins"
```

### Prompts

```
Summarize this academic paper: nins-13-00097.pdf
```
```
Extract the most important key points from the document: nins-13-00097.pdf
```
```
Compare the documents nins-13-00097.pdf and MRM-95-2384.pdf
```
```
Generate study notes for the document MRM-95-2384.pdf
```

---

## How Semantic Search Works

Unlike keyword search (`search_document`), semantic search understands meaning. This is especially useful for scientific literature where the same concept may be expressed using different terminology.

```
User query: "neural network for artery segmentation"
                        ↓
          EmbeddingService (all-MiniLM-L6-v2)
                        ↓
              Query vector [0.23, -0.11, ...]
                        ↓
         FAISS index search (cosine similarity)
                        ↓
     Relevant chunks returned even if they contain
     "CNN", "U-Net", "vessel detection" instead of
     the exact words in the query
```

**To use semantic search:**
1. First index the documents: `Index all documents`
2. Then search: `Search semantically for "attention mechanism in transformer models"`

The FAISS index is **persisted to disk** in `vector_store/` — you do not need to re-index documents after restarting the server.

---

## Architecture Overview

```
AI Agent (Antigravity / Claude Code / etc.)
            |
            | MCP Protocol 
            |
    ┌───────────────┐
    │  FastMCP      │  server.py
    │  Server       │
    └───────┬───────┘
            │
    ┌───────┴────────────────────────────┐
    │              Tools                 │
    │  admin  │  pdf  │ search │  notes  │
    └───────┬────────────────────────────┘
            │
    ┌───────┴────────────────────────────┐
    │             Services               │
    │  PDFService  │  EmbeddingService   │
    │  ChunkService │  VectorService     │
    │  SummaryService                    │
    └───────┬────────────────────────────┘
            │
    ┌───────┴────────────────────────────┐
    │           Storage (disk)           │
    │  documents/  │  vector_store/      │
    │  notes/      │  images/            │
    └────────────────────────────────────┘
```

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'sentence_transformers'`**
```bash
uv add sentence-transformers
```

**`ModuleNotFoundError: No module named 'faiss'`**
```bash
uv add faiss-cpu
```

**Server returns `{"error": "Missing session ID"}`**
The MCP Streamable HTTP protocol requires a POST request, not GET. Use your MCP client normally — do not test with a plain GET request.

**Agent does not show any tools after configuration**
Make sure the server is running (`uv run mcp-server`) before reloading Antigravity. Check the server terminal for connection logs — you should see `Processing request of type ListToolsRequest` when the agent connects.

**Semantic search returns no results**
You must index a document before searching semantically. Run `Index the document <name>.pdf` first.

---

## License

This project was developed as part of a Python course assignment. Example documents are included for demonstration purposes only.
