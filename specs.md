# Document Updater System Specification

## Overview
A web-based system designed to synchronize related technical documents automatically. When a user updates one document (e.g., `requirements.txt`), the system uses an LLM (Google Gemini) to identify and apply corresponding required changes to other conceptually linked documents (e.g., `design.txt`, `deployment.txt`, `api-document.txt`, `ui-document.txt`).

## Architecture
The system follows a standard three-tier architecture:

### 1. Frontend (Vanilla HTML/CSS/JS)
- **Framework**: None (Vanilla).
- **Styling**: Vanilla CSS, leveraging CSS Grid, Flexbox, custom variables, dark mode aesthetic.
- **Components**:
  - Sidebar for listing all available documents retrieved from the backend.
  - Main editor pane for viewing and editing document contents.
- **Interaction**: Uses `fetch` APIs to communicate with the REST backend asynchronously.

### 2. Backend (Python / FastAPI)
- **Framework**: FastAPI for high-performance async REST endpoints.
- **Storage**: In-memory document storage on application startup. Native file operations for persisting to disk.
- **Versioning**: When a document is overwritten, the previous version is moved to a `versions/` directory appended with a timestamp (`YYYYMMDDHHMM`).
- **Endpoints**:
  - `GET /documents`: Return list of filenames.
  - `GET /documents/{filename}`: Return contents of specific file.
  - `POST /update-doc`: Accept filename and new content. Orchestrates saving, versioning, and kicking off LLM synchronization across other documents.

### 3. AI Sync Engine (Google Gemini SDK)
- When a document is updated, the new content and the contents of all *other* documents are passed to the `gemini-2.5-flash` model.
- The model analyzes the semantic implications of the update and returns structured JSON describing which other documents need to change and their revised text.

## Directory Structure
- `/backend`: FastAPI Python source code and `requirements.txt`.
- `/frontend`: HTML, CSS, JS, and `package.json`.
- `/documents`: Live text files representing the system documentation.
- `/versions`: Archival area for previous iterations of the documents.
