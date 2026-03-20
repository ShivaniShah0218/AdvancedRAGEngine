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
        result = asyncio.run(call_mcp_tool("add_org_document", {
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
