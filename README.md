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

## Technologies Used

- **Backend**: Python, FastAPI, ChromaDB
- **Database**: SQLAlchemy, SQLite (development), PostgreSQL/MySQL (production)
- **Authentication**: OAuth2, JWT
- **Async Tasks**: Celery with Redis broker
- **Frontend**: React.js, HTML, CSS, JavaScript
- **Monitoring**: Prometheus, Grafana
- **Embeddings**: SentenceTransformers (all-MiniLM-L6-v2)

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

6. **Start the Celery worker**:
   ```bash
   celery -A backend.worker.celery_worker.celery_app worker -Q ingestion_queue --loglevel=info
   ```

7. **Start the FastAPI backend**:
   ```bash
   python -m backend.run_server
   ```

8. **Start the React frontend**:
   ```bash
   cd frontend-react
   npm install
   npm start
   ```

9. **Access the application**:
   - Frontend: `http://localhost:3001`
   - Backend API: `http://localhost:8000`
   - API Docs: `http://localhost:8000/docs`
   - Prometheus Metrics: `http://localhost:8000/metrics`

## Usage

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
│   ├── worker/           # Celery tasks
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

- **Code Generation**: Utilized Github Copilot  and Kiro to assist in code generation for backend and frontend development, reducing development time and improving code quality.
- **Documentation Generation**: Github Copilot and Kiro is used to generate comprehensive documentation for the API and system architecture, making it easier for developers to understand and contribute to the project.


## License

This project is licensed under the Apache-2.0 License.
