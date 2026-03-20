"""
Delete document from knowledge base using document ID from the metadata of the vector
"""
from backend.knowledge_database.manage_organization_db import get_or_create_collection
from backend.logging_config import get_logger

logger = get_logger(__name__)


def delete_document_embeddings(org_id:str, doc_id:str):
    """
    Delete all vectors associated with a document
    :param org_id: The organization ID
    :param doc_id: The document ID
    :return: True if successful, False otherwise
    """
    # Remove from ChromaDB
    try:
        logger.info(f"Fetching collection for {org_id}")
        collection = get_or_create_collection(org_id)
        # Delete all chunks whose metadata doc_id matches (best-effort)
        logger.info(f"Collection fetched for {org_id}")
        logger.info(f"Fetching all chunks of document {doc_id}")
        results = collection.get(where={"doc_id": doc_id})
        logger.info(f"Found {len(results['ids'])} chunks to delete")
        logger.info(f"Deleting chunks for {doc_id}")
        if results and results.get("ids"):
            collection.delete(ids=results["ids"])
        logger.info(f"Deleted {len(results['ids'])} chunks for {doc_id}")
        return {"deleted":True}
    except Exception as e:
        logger.warning(f"Could not remove vectors for doc {doc_id}: {e}")
        return {"deleted":False}
