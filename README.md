
ScholarFlow AI is a RAG-based AI Research Assistant for students and researchers.

## Main Goal

The system allows users to:
- Create research projects
- Upload PDF papers
- Extract and chunk PDF content
- Store document chunks in ChromaDB
- Ask questions from uploaded papers using RAG
- Search academic/web sources
- Generate citation-backed answers
- Generate research reports and literature reviews

## Tech Stack

Frontend:
- React + Vite
- Tailwind CSS
- React Router
- Axios
- React Markdown

Backend:
- FastAPI
- Python
- Pydantic
- SQLAlchemy
- PostgreSQL

AI:
- Gemini API for answer generation, planning, summarization, and report writing
- Sentence Transformers for local embeddings
- ChromaDB for local vector database

Workflow:
- LangGraph for research workflow orchestration

Documents:
- PyMuPDF for PDF text extraction
- pdfplumber for table extraction if needed

Search:
- Tavily API for web search
- Semantic Scholar API for academic paper search

## Core Backend Modules

- Auth module
- Research project module
- Document upload module
- PDF extraction module
- Embedding module
- ChromaDB vector storage module
- RAG chat module
- LangGraph research workflow
- Citation module
- Report generation module

## LangGraph Workflow

The research graph contains these nodes:

1. Planner Node
   - Creates research plan from user topic.

2. Search Node
   - Searches web and academic sources.

3. Document Node
   - Retrieves uploaded document chunks.

4. RAG Node
   - Retrieves relevant context from ChromaDB.

5. Answer Generator Node
   - Uses Gemini to generate grounded answers.

6. Critic Node
   - Checks whether the answer is supported by sources.

7. Citation Node
   - Formats citations.

8. Report Node
   - Generates final research report.

## Storage

PostgreSQL stores:
- Users
- Research projects
- Documents
- Sources
- Chat messages
- Reports

ChromaDB stores:
- Embedded document chunks
- Metadata including document ID, project ID, page number, and chunk text

Local file system stores:
- Uploaded PDFs in backend/uploads

## Design Principle

The first version should be simple and professional:
- ChromaDB as default vector database
- Gemini as main LLM
- Sentence Transformers as local embedding model
- LangGraph for workflow orchestration
- No unnecessary fallbacks in MVP

Optional later:
- Pinecone cloud mode
- Ollama local LLM fallback
- DuckDuckGo fallback
- arXiv fallback
