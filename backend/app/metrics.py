"""
Prometheus metrics for monitoring the multi-tenant RAG system.
Includes counters and histograms for:
- HTTP requests and latency
- User authentication (login attempts)
- Document management operations (uploads, deletions, queue metrics)
- Vector database operations
- Worker task metrics
"""
from prometheus_client import Counter, Histogram, Gauge

# ── HTTP Request Metrics ──────────────────────────────────────────────────────
REQUEST_COUNT = Counter(
    "app_requests_total",
    "Total HTTP Requests",
    ["method", "endpoint"]
)

REQUEST_LATENCY = Histogram(
    "request_latency_seconds",
    "Request Latency",
    ["endpoint"]
)

# ── Authentication Metrics ────────────────────────────────────────────────────
LOGIN_ATTEMPTS = Counter(
    "login_attempts_total",
    "Total login attempts",
    ["status", "role"]
)

# ── Document Management Metrics ───────────────────────────────────────────────
DOCUMENT_UPLOADS_TOTAL = Counter(
    "document_uploads_total",
    "Total document uploads attempted",
    ["org_id", "status"]
)

DOCUMENT_UPLOAD_SIZE_BYTES = Histogram(
    "document_upload_size_bytes",
    "Document upload size in bytes",
    ["org_id"]
)

DOCUMENT_DELETIONS_TOTAL = Counter(
    "document_deletions_total",
    "Total document deletions attempted",
    ["org_id", "status"]
)

DOCUMENT_QUEUE_LENGTH = Gauge(
    "document_queue_length",
    "Number of documents waiting in ingestion queue",
    ["org_id"]
)

# ── Worker Task Metrics ───────────────────────────────────────────────────────
WORKER_TASKS_TOTAL = Counter(
    "worker_tasks_total",
    "Total worker tasks processed",
    ["task_name", "status"]
)

WORKER_TASK_DURATION_SECONDS = Histogram(
    "worker_task_duration_seconds",
    "Worker task duration in seconds",
    ["task_name"]
)

WORKER_TASK_RETRIES_TOTAL = Counter(
    "worker_task_retries_total",
    "Total worker task retries",
    ["task_name"]
)

# ── Vector Database Metrics ───────────────────────────────────────────────────
CHROMA_COLLECTIONS_TOTAL = Gauge(
    "chroma_collections_total",
    "Number of ChromaDB collections (organizations)"
)

CHROMA_VECTORS_TOTAL = Gauge(
    "chroma_vectors_total",
    "Total vectors in ChromaDB across all collections"
)

CHROMA_ADD_DURATION_SECONDS = Histogram(
    "chroma_add_duration_seconds",
    "Time to add vectors to ChromaDB",
    ["org_id"]
)

CHROMA_QUERY_DURATION_SECONDS = Histogram(
    "chroma_query_duration_seconds",
    "Time to query ChromaDB",
    ["org_id"]
)

# ── Embedding Metrics ─────────────────────────────────────────────────────────
EMBEDDING_CREATION_TOTAL = Counter(
    "embedding_creation_total",
    "Total embeddings created",
    ["model"]
)

EMBEDDING_DURATION_SECONDS = Histogram(
    "embedding_duration_seconds",
    "Time to create embeddings",
    ["chunk_size_bucket"]
)

# ── Knowledge Base Audit Metrics ──────────────────────────────────────────────
KB_AUDIT_LOGS_TOTAL = Counter(
    "kb_audit_logs_total",
    "Total knowledge base audit log entries",
    ["action", "org_id"]
)

# ── Utility Functions for Easy Metrics ───────────────────────────────────────


def increment_document_upload(org_id: str, status: str = "success"):
    """Increment document upload counter with org_id and status."""
    DOCUMENT_UPLOADS_TOTAL.labels(org_id=org_id, status=status).inc()


def observe_document_size(org_id: str, size_bytes: int):
    """Record document upload size."""
    if not org_id or size_bytes <= 0:
        return
    DOCUMENT_UPLOAD_SIZE_BYTES.labels(org_id=org_id).observe(size_bytes)


def increment_document_deletion(org_id: str, status: str = "success"):
    """Increment document deletion counter."""
    DOCUMENT_DELETIONS_TOTAL.labels(org_id=org_id, status=status).inc()


def set_queue_length(org_id: str, length: int):
    """Set current queue length for an org."""
    DOCUMENT_QUEUE_LENGTH.labels(org_id=org_id).set(length)


def increment_worker_task(task_name: str, status: str = "success"):
    """Increment worker task counter."""
    WORKER_TASKS_TOTAL.labels(task_name=task_name, status=status).inc()


def observe_worker_duration(task_name: str, duration: float):
    """Record worker task duration."""
    if not task_name or duration < 0:
        return
    WORKER_TASK_DURATION_SECONDS.labels(task_name=task_name).observe(duration)


def increment_worker_retries(task_name: str):
    """Increment worker task retry counter."""
    WORKER_TASK_RETRIES_TOTAL.labels(task_name=task_name).inc()


def increment_embedding_creation(model: str = "all-MiniLM-L6-v2"):
    """Increment embedding creation counter."""
    EMBEDDING_CREATION_TOTAL.labels(model=model).inc()


def observe_embedding_duration(duration: float, chunk_size: str = "default"):
    """Record embedding creation duration."""
    if duration < 0:
        return
    EMBEDDING_DURATION_SECONDS.labels(chunk_size_bucket=chunk_size).observe(duration)


def increment_kb_audit(action: str, org_id: str):
    """Increment knowledge base audit log counter."""
    KB_AUDIT_LOGS_TOTAL.labels(action=action, org_id=org_id).inc()
