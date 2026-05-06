"""
Defining function for retrieving chunks
"""
from dotenv import load_dotenv
from backend.embedding_model.embeddings import create_embedding
from backend.knowledge_database.manage_organization_db import get_or_create_collection
from backend.logging_config import get_logger


load_dotenv()

logger = get_logger(__name__)


def retrieve_chunks(org_id, query, top_k=5):
    """
    Retrieve top-k chunks from vector db
    
    :param org_id: org_id
    :param query: query prompt
    :param top_k: top k chunks to be retrieved
    :return: list of chunks
    """
    try:
        query_emb = create_embedding(query)
        collection = get_or_create_collection(org_id)
        results = collection.query(query_embeddings=[query_emb], n_results=top_k)
        chunks = results['documents'][0]
        return chunks
    except Exception as e:
        logger.error(f"Error retrieving data: {str(e)}")
        raise e
