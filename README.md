# ScholarFlow AI

ScholarFlow AI is a full-stack AI research assistant for students and researchers who need a structured workspace for document-grounded analysis. It combines PDF ingestion, semantic retrieval, Gemini-powered synthesis, Tavily web search, and report generation inside a project-based workflow.

The application is designed around a simple idea: research should move from scattered files and prompts to a repeatable system where sources, questions, answers, and reports stay connected.

## What It Does

- User registration and login with protected project workspaces
- Project-based research organization
- PDF upload, processing, and indexing
- Local semantic search over uploaded documents with ChromaDB
- Grounded question answering over indexed project material
- Tavily-backed external web search for broader research discovery
- Gemini-powered report generation for summaries, literature reviews, and key findings
- LangGraph orchestration for multi-step research responses
- Saved reports and reusable project context

## Product Overview

ScholarFlow AI is split into two main applications:

- `frontend/`: React + Vite client for authentication, project management, document workflows, Q&A, and report viewing
- `backend/`: FastAPI service for authentication, document processing, retrieval, report generation, orchestration, and persistence

At a high level, the flow is:

1. A user creates an account and signs in
2. A research project is created
3. PDF papers are uploaded and processed
4. Document text is chunked and embedded
5. Chunks are stored in ChromaDB for semantic retrieval
6. Users ask questions or generate reports from indexed project context
7. Gemini generates grounded outputs using retrieved evidence
8. Tavily can be used for web research alongside local document workflows

## Core Capabilities

### 1. Authentication and Project Management
- User registration and login
- Persistent per-user workspaces
- Project creation, listing, viewing, and deletion

### 2. Document Workflow
- Upload PDF documents
- Extract text from PDFs
- Process and index documents into vector storage
- Track document status and page metadata

### 3. Grounded Q&A
- Ask questions against indexed project documents
- Retrieve relevant chunks using semantic similarity
- Generate answers from retrieved evidence instead of ungrounded prompting
- Return supporting source metadata with answers

### 4. Report Generation
- Generate structured reports from project context
- Supported report types:
  - Summary
  - Literature Review
  - Key Findings
- Store generated reports for later review

### 5. Research Search
- Tavily-backed web search endpoint for external discovery
- Project-aware search access under authenticated routes

## Tech Stack

### Frontend
- React
- Vite
- React Router
- Axios
- React Markdown
- Lucide React

### Backend
- FastAPI
- Python
- Pydantic / pydantic-settings
- SQLAlchemy
- PostgreSQL
- SQLite fallback for development

### AI and Retrieval
- Google Gemini for answer generation and report writing
- Sentence Transformers for local embeddings
- ChromaDB for vector storage and semantic retrieval
- LangGraph for workflow orchestration

### Document Processing
- PyMuPDF
- pdfplumber

### External Research
- Tavily API

## Architecture

### Frontend Structure

The frontend is organized around authenticated research workflows:

- `pages/`: top-level application views such as dashboard, auth pages, project workspace, and report detail
- `components/`: reusable application panels such as documents, chat, reports, and layout shell
- `services/api.js`: API layer for backend communication
- `context/AuthContext.jsx`: authentication state and token handling

### Backend Structure

The backend is organized into domain-focused modules:

- `app/api/`: FastAPI route modules
- `app/core/`: settings, prompts, and security helpers
- `app/db/`: SQLAlchemy models, schemas, and session management
- `app/services/`: document, embedding, search, retrieval, Gemini, and reporting services
- `app/agents/`: workflow nodes used by the research graph
- `app/graphs/`: LangGraph state and orchestration graph

## LangGraph Workflow

The currently implemented research graph is composed of these nodes:

1. `planner`
   - Builds a basic research plan from the user query

2. `retriever`
   - Pulls relevant chunks from indexed project documents

3. `answer_generator`
   - Uses Gemini to generate a grounded answer from retrieved context

4. `critic`
   - Reviews the generated answer for quality and support

5. `citation_builder`
   - Formats source references from retrieved evidence

6. `final_response`
   - Assembles the final workflow response payload

Note: there is a placeholder `search_node.py` in the codebase, but the current research graph is centered on document-grounded retrieval rather than external-search-first orchestration.

## Data and Storage

### Relational Database
The backend stores structured application data such as:

- users
- research projects
- documents
- sources
- chat messages
- reports

### Vector Store
ChromaDB stores:

- embedded document chunks
- retrieval metadata such as project, document, page, and chunk identifiers

### Local File Storage
The filesystem stores:

- uploaded PDFs
- local Chroma persistence data
- development SQLite fallback database when PostgreSQL is unavailable in development mode

## API Surface

Main API groups exposed under `/api/v1`:

- `/auth`
- `/research`
- `/documents`
- `/chat`
- `/reports`
- `/search`
- `/health`

Example health endpoint:

- `GET /api/v1/health`

## Environment Configuration

Do not place real secrets in `.env.example`.

Create a local file at:

- `backend/.env`

Use `.env.example` only as a template.

Common backend environment variables:

```env
APP_NAME=ScholarFlow AI
ENVIRONMENT=development
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
DATABASE_URL=postgresql://<db_user>:<db_password>@localhost:5432/<db_name>
JWT_SECRET_KEY=your_local_jwt_secret_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
CHROMA_PERSIST_DIR=./storage/chroma
UPLOAD_DIR=./uploads
TAVILY_API_KEY=your_tavily_api_key_here
TAVILY_MAX_RESULTS=5
SEMANTIC_SCHOLAR_API_KEY=optional_if_used_later
```

## Local Development Setup

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd scholarflow-ai
```

### 2. Start PostgreSQL with Docker (optional but recommended)

```bash
docker compose up -d
```

This starts PostgreSQL on port `5432` using the development configuration in `docker-compose.yml`.

### 3. Set up the backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env` from `backend/.env.example`, then start the API:

```bash
venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 4. Set up the frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server typically runs on:

- `http://localhost:5173`

## Development Notes

- In development, the backend attempts to use `DATABASE_URL` first.
- If PostgreSQL is unavailable, it falls back to a local SQLite database for development continuity.
- The backend loads environment variables from `backend/.env` using an absolute path, so startup is stable even if the server is launched from the repository root.

## Current Status

ScholarFlow AI currently supports the full core loop of:

- authentication
- project creation
- PDF upload and indexing
- grounded Q&A
- report generation
- Tavily web search integration
- polished frontend workspace experience

## Roadmap Ideas

Potential future improvements include:

- deeper external research orchestration inside the LangGraph flow
- stronger citation formatting and export workflows
- richer academic search integrations
- collaborative project features
- report export enhancements
- production deployment configuration and CI/CD

## Security Notes

- Never commit real API keys, tokens, or secrets to the repository
- Keep secrets only in local `.env` files or secure deployment environments
- Rotate any credentials immediately if they are ever exposed

## License

Add your preferred license here before public release.

