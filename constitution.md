<!-- Project Constitution — The Knowledge Extractor -->

This document is the authoritative guide for architecture, security, development standards, and non-goals for "The Knowledge Extractor" repository. As a course demo project, clarity and simplicity are prioritized over enterprise scale.

## Table of contents

- Project Overview
- Core Tech Stack
- Architectural Principles
- Security & Integrity
- Development Standards
- Non-Goals & Constraints

---

## Project Overview

"The Knowledge Extractor" is a local-first web application designed to demonstrate the power of Spec-Kit and Gemini 3. It features:

- **Local Document Watcher** — reads PDF files from a local `./documents` directory.
- **AI Content Engine** — extracts text and uses Gemini 3 to generate structured study materials.
- **Interactive UI** — a React-based flashcard deck and quiz interface with immediate AI feedback.

## Core Tech Stack

- **Frontend:** React (Vite) with Tailwind CSS and Lucide React icons.
- **Backend:** Python 3.10+ with FastAPI.
- **Persistence:** In-memory Python dictionaries or simple local JSON files.
- **AI Integration:** Gemini 3 Flash (via Google Gen AI SDK).
- **Validation:** Pydantic v2 for AI response structuring.

## Architectural Principles

- **Local-First:** The application operates entirely on the local machine and does not connect to external databases or cloud storage (other than the Gemini API).
- **Simplicity over Scale:** Avoid complex folder structures; keep backend logic consolidated (for example, `main.py` for routes, `services.py` for business logic).
- **Asynchronous AI:** All interactions with the Gemini API must be asynchronous (`async`/`await`) to prevent blocking the UI during generation.

## Security & Integrity

- **No Authentication:** The app is open and requires no login (demo-only constraint).
- **Secrets Management:** The Gemini API key must be loaded from a `.env` file. Never commit secrets to the repository.
- **Input Hygiene:** Use Pydantic to validate parsed PDF text before sending it to the LLM.

## Development Standards

- **Testing:** Provide basic unit tests for PDF extraction logic using `pytest`.
- **Formatting:** Use Prettier for frontend code and `black`/`ruff` for Python.
- **Documentation:** Include comments that explain why specific Spec-Kit commands were used (for educational purposes).

## Non-Goals & Constraints

- **No Databases:** Do not install or configure MongoDB, PostgreSQL, or SQLite.
- **No User Accounts:** Do not implement JWT, OAuth, or session cookies.
- **No Redux:** Use React `useState` and `useContext` instead of Redux.
- **No Class Components:** Use React hooks only.
- **No Manual Styling:** All styles must use Tailwind utility classes.

---

**Version:** 1.0.0 (Demo Edition)  •  **Ratified:** 2026-01-09

