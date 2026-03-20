"""
Add document to the knowledge base
"""
import uuid
from backend.knowledge_database.manage_organization_db import get_or_create_collection
from backend.knowledge_database.file_loader import load_document
from backend.knowledge_database.text_chunker import create_chunks
from backend.embedding_model.embeddings import create_embedding
from backend.logging_config import get_logger

logger = get_logger(__name__)


def add_document_embeddings(org_id: str, document_path: str, metadata: dict = {}):
    """
    Add a document to a chroma collection.
    Args:
        org_id (str): The organization id
        document_path (str): Path to the document file
        metadata (dict): Extra metadata to attach to each chunk
    Returns:
        str: The document id (UUID)
    """
    doc_id = str(uuid.uuid4())
    try:
        logger.info(f"Adding document to knowledge base for org {org_id}: {document_path}")
        loaded = load_document(document_path)
        if not loaded:
            raise ValueError(f"Could not load document: {document_path}")

        collection = get_or_create_collection(org_id)
        chunks = create_chunks(loaded)

        for chunk in chunks:
            chunk_id = str(uuid.uuid4())
            chunk_metadata = {**chunk.metadata, **metadata, "doc_id": doc_id}
            collection.add(
                documents=chunk.page_content,
                embeddings=create_embedding(chunk.page_content),
                metadatas=chunk_metadata,
                ids=chunk_id,
            )
            logger.info(f"Chunk {chunk_id} added to collection")

        logger.info(f"All chunks added for doc {doc_id}")
        return {"status":"success","doc_id":doc_id, "message":f"All chunks added for doc {doc_id}"}
    except Exception as e:
        logger.error(f"Error adding document: {str(e)}")
        return {"status":"failed","doc_id":doc_id, "message":f"Error adding document: {str(e)}"}
