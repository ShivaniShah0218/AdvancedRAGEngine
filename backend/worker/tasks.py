"""
This module defines Celery tasks for the backend worker.
"""

import os
import uuid
import json
import time
from dotenv import load_dotenv
from backend.worker.celery_worker import celery_app
from backend.logging_config import get_logger
import asyncio

load_dotenv()

logger = get_logger(__name__)

MCP_URL = os.getenv("MCP_URL")


@celery_app.task(name="backend.worker.tasks.ingest_document", bind=True, max_retries=3)
def ingest_document(self, org_id: str, document_path: str, metadata: dict):
    """
    Celery task: embed a document into the org's vector store via MCP.
    After successful embedding, updates the DocumentRecord with the real doc_id
    and logs the action in the audit log.
    """
    from backend.utils.mcp_client import call_mcp_tool
    from backend.db.database_config import SessionLocal
    from backend.db import models as db_models
    from backend.app.app import _log_kb_action
    from backend.app.metrics import (
        increment_worker_task, observe_worker_duration, increment_worker_retries,
        increment_embedding_creation
    )

    session = SessionLocal()
    start_time = time.time()
    try:
        logger.info(f"Ingesting document for org={org_id}, path={document_path}")

        # Call MCP tool to add document
        result = asyncio.run(call_mcp_tool(MCP_URL,"add_org_document", {
            "org_id": org_id,
            "document": document_path,
            "metadata": metadata
        }))
        result = json.loads(result.content[0].text)
        logger.info(f"Result: {result}")

        # Extract doc_id from result
        if isinstance(result, dict) and result.get("status") == "success":
            doc_id = result.get("doc_id")

            if doc_id:
                logger.info(f"Document ingested: doc_id={doc_id}, org={org_id}")

                # Update DocumentRecord with real doc_id
                record = session.query(db_models.DocumentRecord).filter(
                    db_models.DocumentRecord.doc_id == self.request.id
                ).first()
                if record:
                    record.doc_id = doc_id
                    session.commit()
                    logger.info(f"DocumentRecord updated: task_id={self.request.id}, doc_id={doc_id}")

                # Update audit log with real doc_id
                _log_kb_action(
                    session,
                    "document_added",
                    org_id,
                    metadata.get("performed_by", "unknown"),
                    doc_id,
                    f"Added: {metadata.get('filename', 'unknown')}"
                )

                # Record metrics
                duration = time.time() - start_time
                increment_worker_task("ingest_document", "success")
                observe_worker_duration("ingest_document", duration)
                increment_embedding_creation()

                # Clean up temp file
                if os.path.exists(document_path):
                    os.unlink(document_path)

                return {"status": "success", "doc_id": doc_id}
            else:
                logger.error(f"Could not parse doc_id from MCP response: {result}")
                raise Exception("Could not parse doc_id from MCP response")
        else:
            logger.error(f"MCP tool returned unexpected result: {result}")
            raise Exception(f"MCP tool failed: {result}")

    except Exception as e:
        logger.error(f"Failed to ingest document for org {org_id}: {e}")
        session.rollback()
        increment_worker_retries("ingest_document")
        raise self.retry(exc=e, countdown=2 ** self.request.retries)
    finally:
        session.close()


@celery_app.task(name="backend.worker.tasks.process_rag_query", bind=True, max_retries=2)
def process_rag_query(self, query_id: str, query_text: str, org_id: str):
    """
    Celery task: run the full RAG pipeline for a user query.
    Updates RAGQuery status, writes step logs to RAGQueryLog, and records RAGMetrics.
    """
    from backend.db.database_config import SessionLocal
    from backend.db import models as db_models
    from backend.rag.rag_pipeline import rag_pipeline
    from backend.app.metrics import (
        increment_rag_query, observe_rag_duration,
        increment_guardrail_block, observe_retrieval_chunks
    )
    from datetime import datetime

    session = SessionLocal()
    start_time = time.time()

    def _log_step(step: str, status: str, details: str = "", duration_ms: int = None):
        entry = db_models.RAGQueryLog(
            query_id=query_id, step=step, status=status,
            details=details, duration_ms=duration_ms
        )
        session.add(entry)
        session.commit()

    try:
        # Mark as processing
        record = session.query(db_models.RAGQuery).filter_by(query_id=query_id).first()
        if not record:
            raise Exception(f"RAGQuery {query_id} not found")
        record.status = "processing"
        session.commit()
        logger.info(f"Processing RAG query {query_id} for org={org_id}")

        # Run pipeline
        result = rag_pipeline(query_text, org_id)

        duration_ms = int((time.time() - start_time) * 1000)
        guardrail_blocked = "error" in result and "guardrail" in result.get("error", "").lower()

        if "error" in result:
            record.status = "failed"
            record.error_message = result["error"]
            record.completed_at = datetime.utcnow()
            session.commit()
            _log_step("pipeline", "failed", result["error"], duration_ms)
            increment_rag_query(org_id, "failed")
            if guardrail_blocked:
                stage = "query" if "query" in result["error"] else "context" if "context" in result["error"] else "response"
                increment_guardrail_block(org_id, stage)
            return {"status": "failed", "error": result["error"]}

        # Success — persist answer
        record.status = "done"
        record.answer = result.get("answer", "")
        record.completed_at = datetime.utcnow()
        session.commit()

        # Write step logs
        _log_step("retrieval", "success", json.dumps({"count": result.get("retrieved_count")}))
        _log_step("reranking", "success", json.dumps({"count": result.get("reranked_count")}))
        _log_step("generation", "success", json.dumps({"answer_length": len(record.answer)}))
        _log_step("evaluation", "success", json.dumps(result.get("rouge_scores", {})))

        # Write metrics
        rouge = result.get("rouge_scores") or {}
        metrics = db_models.RAGMetrics(
            query_id=query_id,
            org_id=org_id,
            retrieval_count=result.get("retrieved_count"),
            reranked_count=result.get("reranked_count"),
            rouge1=str(rouge.get("rouge1", "")),
            rougeL=str(rouge.get("rougeL", "")),
            total_duration_ms=duration_ms,
            guardrail_blocked=False,
        )
        session.add(metrics)
        session.commit()

        # Prometheus
        increment_rag_query(org_id, "success")
        observe_rag_duration(org_id, time.time() - start_time)
        observe_retrieval_chunks(org_id, result.get("retrieved_count", 0))

        logger.info(f"RAG query {query_id} completed in {duration_ms}ms")
        return {"status": "done", "query_id": query_id}

    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        logger.error(f"RAG query {query_id} failed: {e}")
        session.rollback()
        try:
            record = session.query(db_models.RAGQuery).filter_by(query_id=query_id).first()
            if record:
                record.status = "failed"
                record.error_message = str(e)
                record.completed_at = datetime.utcnow()
                session.commit()
            _log_step("pipeline", "error", str(e), duration_ms)
        except Exception:
            pass
        increment_rag_query(org_id, "failed")
        raise self.retry(exc=e, countdown=5 * (self.request.retries + 1))
    finally:
        session.close()
