"""
This module defines the MCP tools for the RAG pipeline.
It provides tools for retrieval, reranking, generation, and evaluation.
"""
from fastmcp import FastMCP
from backend.logging_config import get_logger
from backend.rag.retrieval import retrieve_chunks
from backend.rag.reranking import rerank_chunks
from backend.rag.generate import generate_answer
from backend.rag.evaluate import evaluate_rouge

logger = get_logger(__name__)
rag_mcp = FastMCP("RAG Pipeline MCP server")


@rag_mcp.tool()
def retrieve(query: str, org_id: str, top_k: int = 5):
    """
    Retrieve relevant chunks for a query from the knowledge base.
    
    Args:
        query: The search query
        org_id: The organization ID
        top_k: Number of chunks to retrieve (default: 5)
    
    Returns:
        List of retrieved chunk texts
    """
    try:
        logger.info(f"Retrieving {top_k} chunks for query: {query[:50]}...")
        chunks = retrieve_chunks(org_id, query, top_k)
        logger.info(f"Retrieved {len(chunks)} chunks")
        return {"chunks": chunks, "count": len(chunks)}
    except Exception as e:
        logger.error(f"Error in retrieve: {e}")
        return {"error": str(e)}


@rag_mcp.tool()
def rerank(query: str, chunks: list[str]):
    """
    Rerank chunks based on relevance to the query.
    
    Args:
        query: The search query
        chunks: List of chunk texts to rerank
    
    Returns:
        Reranked chunks with scores
    """
    try:
        logger.info(f"Reranking {len(chunks)} chunks for query: {query[:50]}...")
        reranked_chunks, scores = rerank_chunks(query, chunks)
        logger.info(f"Reranked chunks, top score: {max(scores) if scores else 0}")
        return {
            "chunks": reranked_chunks,
            "scores": scores,
            "count": len(reranked_chunks)
        }
    except Exception as e:
        logger.error(f"Error in rerank: {e}")
        return {"error": str(e)}


@rag_mcp.tool()
def generate(query: str, context: str):
    """
    Generate an answer based on the query and context chunks.
    
    Args:
        query: The search query
        context: Context string (first chunk)
    
    Returns:
        Generated answer
    """
    try:
        logger.info(f"Generating answer for query: {query[:50]}...")
        logger.info(f"Context type: {type(context)}, value: {context[:100] if isinstance(context, str) else context}")
        # If context is a list, extract the first element
        if isinstance(context, list):
            context_text = context[0] if context else ""
        elif isinstance(context, str):
            context_text = context
        else:
            context_text = str(context)
        answer = generate_answer(context_text, query)
        if answer is None:
            logger.error("Generate returned None")
            return {"error": "Failed to generate answer"}
        logger.info(f"Answer generated, length: {len(answer)}")
        return {"answer": answer, "context_length": len(context_text)}
    except Exception as e:
        logger.error(f"Error in generate: {e}")
        return {"error": str(e)}


@rag_mcp.tool()
def evaluate(generated_answer: str, ground_truth: str):
    """
    Evaluate the generated answer using ROUGE metrics.
    
    Args:
        generated_answer: The generated answer
        ground_truth: The ground truth answer for comparison
    
    Returns:
        ROUGE scores (rouge1, rougeL)
    """
    try:
        logger.info("Evaluating generated answer...")
        if isinstance(ground_truth, list):
            ground_truth = ground_truth[0] if ground_truth else ""
        elif isinstance(ground_truth, str):
            ground_truth = ground_truth
        else:
            ground_truth = str(ground_truth)
        scores = evaluate_rouge(generated_answer, ground_truth)
        if scores:
            logger.info(f"ROUGE scores: {scores}")
            return scores
        return {"error": "Evaluation failed"}
    except Exception as e:
        logger.error(f"Error in evaluate: {e}")
        return {"error": str(e)}

