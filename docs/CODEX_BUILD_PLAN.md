
---

## `docs/CODEX_BUILD_PLAN.md`

Paste this:

```md
# Codex Build Plan for ScholarFlow AI

You are building ScholarFlow AI, a RAG-based AI Research Assistant.

Build the system step by step. Do not over-engineer. Prioritize clean architecture, working APIs, and clear separation of concerns.

## Current Goal

Implement the MVP.

## MVP Features

1. Backend setup with FastAPI
2. PostgreSQL database connection
3. SQLAlchemy models
4. JWT authentication
5. Research project CRUD
6. PDF upload
7. PDF text extraction with PyMuPDF
8. Text chunking
9. Local embeddings using Sentence Transformers
10. ChromaDB vector storage
11. RAG question-answering using Gemini
12. LangGraph research workflow
13. Basic React dashboard
14. Research workspace UI
15. PDF upload UI
16. Chat with uploaded documents
17. Generate basic research report

## Important Architecture Rules

- Use FastAPI for backend APIs.
- Use React + Vite + Tailwind for frontend.
- Use PostgreSQL for app data.
- Use ChromaDB for vector storage.
- Use Sentence Transformers for embeddings.
- Use Gemini API for LLM responses.
- Use LangGraph to orchestrate research workflow.
- Keep Pinecone, Ollama, DuckDuckGo, and arXiv as future optional improvements.
- Do not implement unnecessary fallbacks in MVP.
- Keep services modular.

## Backend Structure

Use this structure:

backend/app/
- api/
- agents/
- core/
- db/
- graphs/
- services/

## Required Services

Create these services:

- gemini_service.py
- embedding_service.py
- chroma_service.py
- pdf_service.py
- search_service.py
- citation_service.py
- export_service.py

## Required API Route Files

Create these route files:

- auth_routes.py
- research_routes.py
- document_routes.py
- chat_routes.py
- report_routes.py

## Required LangGraph

Create `backend/app/graphs/research_graph.py`.

The graph should include:

- planner_node
- document_retrieval_node
- rag_node
- answer_generation_node
- critic_node
- citation_node
- report_node

The MVP graph can be simple but should be extendable.

## Database Models

Create SQLAlchemy models for:

- User
- ResearchProject
- Document
- Source
- ChatMessage
- Report

## Development Order

Follow this order:

### Step 1: Backend Foundation

- Setup FastAPI app
- Setup CORS
- Setup config using pydantic-settings
- Setup PostgreSQL database connection
- Create SQLAlchemy models
- Create database tables

### Step 2: Authentication

- Create register endpoint
- Create login endpoint
- Create JWT token generation
- Create current user dependency

### Step 3: Research Projects

- Create project CRUD endpoints
- Connect projects to authenticated user

### Step 4: Document Upload

- Upload PDF to local uploads folder
- Save document metadata in PostgreSQL
- Extract text using PyMuPDF
- Chunk text

### Step 5: Embeddings and ChromaDB

- Generate embeddings using Sentence Transformers
- Store chunks in ChromaDB with metadata
- Retrieve top relevant chunks by query

### Step 6: RAG Chat

- Create `/chat/ask`
- Retrieve relevant chunks from ChromaDB
- Send question + context to Gemini
- Return answer with sources

### Step 7: LangGraph Workflow

- Create graph nodes
- Use graph for `/research/start`
- Generate plan, retrieve context, answer, critique, citations, and report

### Step 8: Frontend

- Create dashboard
- Create login/register pages
- Create research project page
- Create document upload page
- Create chat panel
- Create report page

### Step 9: Polish

- Add loading states
- Add error handling
- Add clean UI
- Add README instructions

## Coding Standards

- Keep code clean and readable.
- Use environment variables.
- Do not hardcode API keys.
- Use Pydantic schemas for request/response.
- Add helpful comments only where needed.
- Return clear error messages.
- Keep functions small.
- Avoid unnecessary complexity.

## MVP Success Criteria

The MVP is successful when:

1. User can register/login.
2. User can create a research project.
3. User can upload a PDF.
4. System extracts and embeds PDF content.
5. User can ask questions from uploaded PDF.
6. System answers using Gemini with retrieved ChromaDB context.
7. System returns source chunks/page metadata.
8. User can generate a basic research report.