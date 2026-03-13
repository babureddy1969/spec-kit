# SpecIt Document Synchronization System

SpecIt is an intelligent document management system designed to keep related technical specifications in sync. When a user updates a single document (e.g., changing requirements), the system leverages the Google Gemini Large Language Model (LLM) to automatically analyze and apply necessary updates to all other related conceptual documents (e.g., design, UI, API specifications).

## Features

- **Document Editing:** View and edit plain text documents via a sleek, dark-themed web interface.
- **Smart Synchronization:** Powered by Google Gemini (`gemini-2.5-flash`), updates in one file logically cascade to other documents without manual intervention.
- **Automatic Versioning:** Whenever a file is updated, its previous state is automatically archived into a `versions/` directory and timestamped.
- **In-Memory Caching:** Fast retrieval of documents via an in-memory dictionary on the backend.

## Project Structure

- `frontend/`: Vanilla HTML/CSS/JS single-page application and its local server configuration (`package.json`).
- `backend/`: FastAPI Python server containing the core REST endpoints and LLM integration logic.
- `documents/`: The active, live text files the system manages.
- `versions/`: Archival folder storing timestamped backups whenever a document is modified.
- `.specify/`: Directory containing project specifications, planning notes, and task checklists.

## Prerequisites

To run this application locally, you will need:
- Node.js (for the frontend static server)
- Python 3.9+ (for the backend server)
- A valid Google Gemini API Key. Set this as an environment variable: `export GEMINI_API_KEY="your_api_key_here"`

## Running the Application

### 1. Start the Backend Server

Navigate to the `backend/` directory, create a virtual environment, install the dependencies, and run the server:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

The backend API will be available at `http://localhost:8000`.

### 2. Start the Frontend Server

Navigate to the `frontend/` directory, install the local packages, and start the static file server:

```bash
cd frontend
npm install
npm start
```

The frontend interface will be available at `http://localhost:8080`.

## Architecture Details

- **Frontend:** Built with standard HTML5, CSS Variables for theming (CSS Grid & Flexbox), and modular JavaScript utilizing native robust `fetch` API for network requests. No bulky frameworks.
- **Backend:** Built with `FastAPI` to provide high-performance asynchronous endpoints (`GET /documents`, `GET /documents/{filename}`, `POST /update-doc`).
- **LLM Integration:** Utilizes the `google-genai` Python SDK to programmatically submit prompts consisting of updated file contents and surrounding system context. It expects valid structural JSON responses indicating which other nodes (documents) need mutation.
