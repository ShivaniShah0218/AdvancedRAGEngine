"""
Defining the RAG pipeline function
"""
import asyncio
import json
import os
from dotenv import load_dotenv
from backend.logging_config import get_logger
from backend.utils.mcp_client import call_mcp_tool

load_dotenv()

logger = get_logger(__name__)
GUARDRAILS_URL = os.getenv("GUARDRAILS_URL")
RAG_URL = os.getenv("RAG_URL")


def _parse(call_result) -> dict:
    """Parse a CallToolResult into a plain dict."""
    try:
        return json.loads(call_result.content[0].text)
    except Exception as e:
        logger.error(f"Failed to parse MCP result: {e} — raw: {call_result}")
        return {"error": f"Failed to parse MCP result: {e}"}


def rag_pipeline(query, org_id):
    try:
        if not query:
            raise ValueError("Query cannot be empty")

        # ── Query guardrail ───────────────────────────────────────────────────
        logger.info("Validating input query via guardrail")
        result = _parse(asyncio.run(call_mcp_tool(GUARDRAILS_URL, "query_guardrail", {"query": query})))
        if "error" in result:
            return result
        if result.get("action") == "block" or result.get("allowed") is False:
            logger.warning(f"Query blocked by guardrail: {result.get('reason')}")
            return {"error": f"Query blocked by guardrail: {result.get('reason')}"}
        logger.info("Input query passed guardrail")

        # ── 1. Retrieve ───────────────────────────────────────────────────────
        logger.info(f"Retrieving chunks for query: {query[:60]}")
        retrieved = _parse(asyncio.run(call_mcp_tool(RAG_URL, "retrieve", {"org_id": org_id, "query": query})))
        if "error" in retrieved:
            return retrieved

        # ── 2. Rerank ─────────────────────────────────────────────────────────
        logger.info("Reranking chunks")
        reranked = _parse(asyncio.run(call_mcp_tool(RAG_URL, "rerank", {"chunks": retrieved["chunks"], "query": query})))
        if "error" in reranked:
            return reranked
        logger.info(f"Reranked {len(reranked['chunks'])} chunks: {reranked['chunks'][0]}")

        # ── Context guardrail ─────────────────────────────────────────────────
        logger.info("Validating context via guardrail")
        result = _parse(asyncio.run(call_mcp_tool(GUARDRAILS_URL, "context_guardrail", {
            "query": query,
            "context_chunks": [{"text": reranked["chunks"][0]}] if reranked["chunks"] else []
        })))
        if "error" in result:
            return result
        if result.get("action") == "block" or result.get("safe") is False:
            logger.warning(f"Context blocked by guardrail: {result.get('reason', result.get('issues'))}")
            return {"error": f"Context blocked by guardrail: {result.get('reason', '')}"}
        logger.info("Context passed guardrail")

        # ── 3. Generate ───────────────────────────────────────────────────────
        logger.info("Generating answer")
        generated = _parse(asyncio.run(call_mcp_tool(RAG_URL, "generate", {
            "context":reranked["chunks"][0] if reranked["chunks"] else "",
            "query": query
        })))
        if "error" in generated:
            return generated

        # ── Response guardrail ────────────────────────────────────────────────
        logger.info("Validating response via guardrail")
        result = _parse(asyncio.run(call_mcp_tool(GUARDRAILS_URL, "response_guardrail", {
            "query": query,
            "context_chunks": [{"text": reranked["chunks"][0]}] if reranked["chunks"] else [],
            "response": generated["answer"]
        })))
        if "error" in result:
            return result
        if result.get("action") == "block" or result.get("valid") is False or result.get("grounded") is False:
            logger.warning(f"Response blocked by guardrail: {result.get('reason', result.get('issues'))}")
            return {"error": f"Response blocked by guardrail: {result.get('reason', '')}"}
        logger.info("Response passed guardrail")

        # ── 4. Evaluate ───────────────────────────────────────────────────────
        logger.info("Evaluating answer")
        evaluation = _parse(asyncio.run(call_mcp_tool(RAG_URL, "evaluate", {
            "ground_truth": reranked["chunks"][0], #reranked["chunks"] if reranked["chunks"] else "",
            "generated_answer": generated["answer"]
        })))

        return {
            "answer": generated["answer"],
            "chunks": reranked["chunks"],
            "scores": reranked.get("scores", []),
            "rouge_scores": evaluation,
            "retrieved_count": retrieved.get("count", len(retrieved["chunks"])),
            "reranked_count": reranked.get("count", len(reranked["chunks"])),
        }

    except Exception as e:
        logger.error(f"Error in RAG pipeline: {str(e)}")
        return {"error": str(e)}
