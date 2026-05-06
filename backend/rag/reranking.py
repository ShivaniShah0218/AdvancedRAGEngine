"""
Defining function for reranking chunks using the reranker model
"""
from dotenv import load_dotenv
from backend.rag.config import reranker as _reranker_model
from backend.logging_config import get_logger

load_dotenv()

logger = get_logger(__name__)


def rerank_chunks(query, chunks):
    """
    Rerank chunks based on their relevance to the query
    Args:
        query (str): The search query
        chunks (list): List of text chunks to rerank
    Returns:
        tuple: Reranked chunks and their scores
    """
    try:
        logger.info("Reranking chunks")
        scores = _reranker_model.predict([(query, chunk) for chunk in chunks])
        reranked_chunks = [c for _, c in sorted(zip(scores, chunks), reverse=True)]
        logger.info(f"Chunks reranked, top score: {max(scores):.4f}")
        return reranked_chunks, scores.tolist()
    except Exception as e:
        logger.error(f"Error in reranking: {str(e)}")
        raise e
