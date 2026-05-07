# AdvancedRAGEngine

Advanced End-to-End RAG System

This repository contains an advanced multi-tenant end-to-end Retrieval-Augmented Generation (RAG) system. The system is designed to be flexible, scalable, and easy to deploy, making it suitable for a wide range of applications.

## Features

- **Multi-Tenancy**: Supports multiple tenants with isolated data and configurations
- **Document Management**: Upload, delete, and track documents in organization knowledge bases
- **Role-Based Access Control**: Admin, Editor, and Viewer roles with granular permissions
- **Async Processing**: Celery workers for document embedding and vector storage
- **Prometheus Monitoring**: Comprehensive metrics for HTTP requests, authentication, document operations, and worker tasks
- **Audit Logging**: Tracks all knowledge base actions (document adds, deletions)
- **Vector Database**: ChromaDB for persistent vector storage with organization-specific collections
- **RAG Pipeline**: End-to-end retrieval-augmented generation with query validation, retrieval, reranking, answer generation, and response evaluation
- **Guardrails**: Multi-layer security with query, context, and response validation using rule-based patterns, NLI models, and zero-shot classification
- **MCP Integration**: Model Context Protocol servers for RAG operations and document management

## Technologies Used

- **Backend**: Python, FastAPI, ChromaDB
- **Database**: SQLAlchemy, SQLite (development), PostgreSQL/MySQL (production)
- **Authentication**: OAuth2, JWT
- **Async Tasks**: Celery with Redis broker
- **Frontend**: React.js, HTML, CSS, JavaScript
- **Monitoring**: Prometheus, Grafana
- **Embeddings**: SentenceTransformers (all-MiniLM-L6-v2)
- **Reranking**: CrossEncoder models
- **LLM**: AutoModelForCausalLM (e.g., Llama, Mistral)
- **Evaluation**: ROUGE metrics
- **Guardrails**: NLI models, zero-shot classification
- **MCP**: Model Context Protocol for distributed services

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                            │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────────┐   │
│  │  Dashboard   │  │   Modals     │  │  Knowledge Base UI      │   │
│  └──────────────┘  └──────────────┘  └─────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Backend API (FastAPI)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────────┐   │
│  │  Auth        │  │  Org/Users   │  │  Document Management    │   │
│  │  Endpoints   │  │  Endpoints   │  │  Endpoints              │   │
│  └──────────────┘  └──────────────┘  └─────────────────────────┘   │
│                                    │                                │
│  ┌─────────────────────────────────┴───────────────────────────┐   │
│  │                    Celery Worker                             │   │
│  │  ┌────────────────────────────────────────────────────────┐  │   │
│  │  │  Document Ingestion Task                               │  │   │
│  │  │  - Load document                                       │  │   │
│  │  │  - Chunk text                                          │  │   │
│  │  │  - Create embeddings                                   │  │   │
│  │  │  - Store in ChromaDB                                   │  │   │
│  │  └────────────────────────────────────────────────────────┘  │   │
│  └───────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Data Layer                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────────┐   │
│  │  SQLite      │  │  ChromaDB    │  │  Redis (Celery)         │   │
│  │  (Users,Orgs)│  │  (Vectors)   │  │  (Task Queue)           │   │
│  └──────────────┘  └──────────────┘  └─────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

## Key Components

### Backend (`backend/`)

- **`app/app.py`**: FastAPI application with all REST endpoints
- **`db/models.py`**: SQLAlchemy models (Organization, User, DocumentRecord, KnowledgeBaseAuditLog)
- **`db/utils.py`**: Authentication utilities (password hashing, user lookup, permission checks)
- **`embedding_model/`**: SentenceTransformer embeddings
- **`knowledge_database/`**: Document ingestion, chunking, and ChromaDB integration
- **`worker/`**: Celery tasks for async document processing
- **`rag/`**: RAG pipeline components
  - **`rag_pipeline.py`**: Main RAG pipeline orchestrating retrieval, reranking, generation, and evaluation
  - **`retrieval.py`**: Vector retrieval from ChromaDB
  - **`reranking.py`**: Cross-encoder reranking of retrieved chunks
  - **`generate.py`**: LLM-based answer generation with context
  - **`evaluate.py`**: ROUGE-based evaluation of generated answers
  - **`config.py`**: Model initialization (LLM, tokenizer, reranker, evaluator)
  - **`mcp_server.py`**: MCP server for RAG operations (retrieve, rerank, generate, evaluate)
- **`rag/guardrails/`**: Security guardrails
  - **`guardrails_engine.py`**: Multi-layer guardrail engine with rule-based, NLI, and classifier checks
  - **`query_relevant_guardrail.py`**: Query relevance validation
  - **`context_guardrail.py`**: Context safety and relevance validation
  - **`response_guardrail.py`**: Response safety and groundedness validation
  - **`mcp_server.py`**: MCP server for guardrail validation (query, context, response)
- **`utils/`**: Utility functions
  - **`model_download.py`**: Model download utilities
  - **`model_download_check.py`**: Model download verification
  - **`mcp_client.py`**: MCP client for calling remote tools

### Frontend (`frontend-react/`)

- **`src/components/Dashboard.jsx`**: Main dashboard with role-based views
- **`src/components/KnowledgeBaseModal.jsx`**: Document upload and audit log UI
- **`src/api.js`**: API client for all backend interactions

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ShivaniShah0218/AdvancedRAGEngine.git
   cd AdvancedRAGEngine
   ```

2. **Set up Python environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables** (`.env`):
   ```env
   DATABASE_URL=sqlite:///./rag_user_auth.db
   INITIAL_ADMIN_USERNAME=admin
   INITIAL_ADMIN_PASSWORD=your_secure_password
   JWT_SECRET=your_jwt_secret_key
   JWT_EXPIRE_S=1800
   ALGORITHM=HS256
   MCP_URL=http://localhost:8001/mcp
   REDIS_URL=redis://localhost:6379/0
   CHROMA_DIRECTORY=./rag_knowledge_database
   TMP_PATH=./backend/tmp_files
   ```

4. **Initialize the database**:
   ```bash
   python -c "from backend.db.database_config import engine, Base; from backend.db import models; Base.metadata.create_all(bind=engine)"
   ```

5. **Start Redis** (required for Celery):
   ```bash
   redis-server
   ```

6. **Start the MCP servers** (in separate terminals):
   ```bash
   # Document manager MCP server
   python -m backend.knowledge_database.mcp_server

   # RAG pipeline MCP server
   python -m backend.rag.mcp_server

   # Guardrails MCP server
   python -m backend.rag.guardrails.mcp_server
   ```

7. **Start the Celery worker** (in a separate terminal):
   ```bash
   # Document ingestion worker
   celery -A backend.worker.celery_worker.celery_app worker -Q ingestion_queue --loglevel=info --pool=threads --concurrency=4

   # RAG query worker
   celery -A backend.worker.celery_worker.celery_app worker -Q rag_query_queue --loglevel=info --pool=threads --concurrency=4

   ```

8. **Start the FastAPI backend**:
   ```bash
   python -m backend.run_server
   ```

9. **Start the React frontend**:
   ```bash
   cd frontend-react
   npm install
   npm start
   ```

10. **Access the application**:
   - Frontend: `http://localhost:3001`
   - Backend API: `http://localhost:8000`
   - API Docs: `http://localhost:8000/docs`
   - Prometheus Metrics: `http://localhost:8000/metrics`

## Usage

### RAG Pipeline

The RAG pipeline processes queries through multiple stages:

1. **Query Guardrail**: Validates input for security issues using rule-based patterns and zero-shot classification
2. **Retrieve**: Fetches top-k relevant chunks from ChromaDB using vector embeddings
3. **Rerank**: Re-ranks chunks using a cross-encoder model for better relevance
4. **Context Guardrail**: Validates retrieved context for safety and relevance
5. **Generate**: Uses LLM to generate answers based on context and query
6. **Response Guardrail**: Validates generated response for safety and groundedness
7. **Evaluate**: Computes ROUGE scores to measure answer quality

### Authentication

- **Admin**: Full access to all organizations, can create organizations and manage all users
- **Editor**: Can manage documents in their organization, create users, view audit logs
- **Viewer**: Read-only access to their organization's data

### Document Management

1. **Upload a document**:
   - Login as an Editor or Admin
   - Click "📚 Knowledge Base" on your organization card
   - Select a file (PDF, TXT, DOC, DOCX, CSV, XLSX, XLS)
   - The document is queued for embedding and stored in ChromaDB

2. **View documents**:
   - In the Knowledge Base modal, switch to the "Documents" tab
   - See all uploaded documents with upload metadata

3. **Delete a document**:
   - Click "🗑 Delete" next to any document
   - Confirms deletion from both database and vector store

4. **Audit logs**:
   - Switch to the "Audit Log" tab in Knowledge Base modal
   - See all document add/delete actions with timestamps and performers

### RAG Query

To query the knowledge base:

1. Submit a question through the frontend
2. The query passes through guardrails for security validation
3. Relevant chunks are retrieved from the vector database
4. Chunks are reranked for relevance
5. Context is validated for safety
6. LLM generates an answer based on context
7. Response is validated for safety and groundedness
8. Answer quality is evaluated using ROUGE metrics

### Monitoring

- **Prometheus metrics** are available at `/metrics` endpoint
- Key metrics include:
  - `app_requests_total` — HTTP request counts
  - `login_attempts_total` — Authentication attempts
  - `document_uploads_total` — Document upload attempts
  - `worker_tasks_total` — Celery task processing
  - `embedding_creation_total` — Embedding generation

- **Grafana dashboards** can be configured to visualize these metrics

## API Endpoints

### Authentication
- `POST /token` — Login, returns JWT token

### Organizations
- `POST /admin/orgs` — Create organization (admin only)
- `GET /orgs` — List organizations

### Users
- `POST /orgs/{org_id}/users` — Create user
- `GET /orgs/{org_id}/users` — List users
- `DELETE /orgs/{org_id}/users/{username}` — Delete user

### Documents
- `POST /orgs/{org_id}/documents` — Upload document (editor/admin)
- `GET /orgs/{org_id}/documents` — List documents (editor/admin)
- `DELETE /orgs/{org_id}/documents/{doc_id}` — Delete document (editor/admin)
- `GET /orgs/{org_id}/kb-audit-logs` — Get audit logs (editor/admin)

### System
- `GET /metrics` — Prometheus metrics
- `GET /task-status/{task_id}` — Check async task status

## Project Structure

```
AdvancedRAGEngine/
├── backend/
│   ├── app/              # FastAPI application
│   │   ├── app.py        # Main API endpoints
│   │   ├── metrics.py    # Prometheus metrics
│   │   └── schemas.py    # Pydantic schemas
│   ├── db/               # Database models and utilities
│   │   ├── models.py     # SQLAlchemy models
│   │   ├── utils.py      # Auth utilities
│   │   └── database_config.py
│   ├── embedding_model/  # SentenceTransformer integration
│   ├── knowledge_database/  # Document ingestion and ChromaDB
│   │   ├── mcp_server.py     # Document manager MCP server
│   │   ├── add_document.py   # Document ingestion
│   │   ├── delete_document.py # Document deletion
│   │   ├── file_loader.py    # File loading utilities
│   │   ├── manage_organization_db.py # ChromaDB management
│   │   └── text_chunker.py   # Text chunking utilities
│   ├── worker/           # Celery tasks
│   │   ├── celery_worker.py  # Celery app configuration
│   │   └── tasks.py          # Task definitions
│   ├── rag/              # RAG pipeline components
│   │   ├── rag_pipeline.py   # Main pipeline orchestrator
│   │   ├── retrieval.py      # Vector retrieval
│   │   ├── reranking.py      # Cross-encoder reranking
│   │   ├── generate.py       # LLM answer generation
│   │   ├── evaluate.py       # ROUGE evaluation
│   │   ├── config.py         # Model configuration
│   │   ├── mcp_server.py     # RAG MCP server
│   │   └── guardrails/       # Security guardrails
│   │       ├── guardrails_engine.py   # Main guardrail engine
│   │       ├── query_relevant_guardrail.py # Query validation
│   │       ├── context_guardrail.py      # Context validation
│   │       ├── response_guardrail.py     # Response validation
│   │       └── mcp_server.py             # Guardrail MCP server
│   ├── utils/            # Utility functions
│   │   ├── model_download.py      # Model download utilities
│   │   ├── model_download_check.py # Model verification
│   │   └── mcp_client.py          # MCP client
│   ├── logging_config.py
│   └── run_server.py
├── frontend-react/       # React application
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── api.js        # API client
│   │   └── styles/
│   └── public/
├── venv/                 # Python virtual environment
├── requirements.txt
├── README.md
└── .env
```

## AI Assistance or Development Tools

- **Code Generation**: Utilized GitHub Copilot and Kiro to assist in code generation for backend and frontend development, reducing development time and improving code quality.
- **Documentation Generation**: GitHub Copilot and Kiro are used to generate comprehensive documentation for the API and system architecture, making it easier for developers to understand and contribute to the project.
- **RAG Pipeline**: Implements a multi-stage retrieval-augmented generation pipeline with guardrails for security and evaluation metrics for quality assurance.
- **MCP Integration**: Uses Model Context Protocol to enable distributed microservices for RAG operations and document management.

