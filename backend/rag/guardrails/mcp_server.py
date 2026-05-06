"""
MCP tools for guardrail validation of queries, context, and responses.
"""
import json
from fastmcp import FastMCP
from backend.logging_config import get_logger
from backend.rag.config import engine

logger = get_logger(__name__)
guardrails_mcp = FastMCP("GuardRails MCP server")


@guardrails_mcp.tool()
def query_guardrail(query: str) -> str:
    """Validate input query for security issues. Returns JSON string."""
    try:
        logger.info(f"Validating query: {query[:80]}")
        result = engine.evaluate_query(query)
        logger.info(f"Query guardrail result: {result}")
        if isinstance(result, dict):
            if result.get("action") == "block":
                logger.warning(f"Query blocked: {result.get('reason')}")
            return json.dumps(result)
        return json.dumps({"allowed": False, "risk": "high", "reason": str(result), "action": "block"})
    except Exception as e:
        logger.error(f"Error in query_guardrail: {e}")
        return json.dumps({"allowed": False, "risk": "high", "reason": str(e), "action": "block"})


@guardrails_mcp.tool()
def context_guardrail(query: str, context_chunks: list[dict]) -> str:
    """Validate retrieved context for safety. Returns JSON string."""
    try:
        logger.info(f"Validating context for query: {query[:60]}")
        # Use only the first chunk for context guardrail
        context_text = context_chunks[0].get("text", "") if context_chunks else ""
        result = engine.evaluate_context(query, context_text)
        logger.info(f"Context guardrail result: {result}")
        if isinstance(result, dict):
            if result.get("action") == "block":
                logger.warning(f"Context blocked: {result.get('reason')}")
                return json.dumps({"safe": False, "issues": result.get("issues", [result.get("reason", "blocked")]), "action": "block"})
            return json.dumps({"safe": True, "issues": [], "action": "allow"})
        return json.dumps({"safe": False, "issues": [str(result)], "action": "block"})
    except Exception as e:
        logger.error(f"Error in context_guardrail: {e}")
        return json.dumps({"safe": False, "issues": [str(e)], "action": "block"})


@guardrails_mcp.tool()
def response_guardrail(query: str, context_chunks: list[dict], response: str) -> str:
    """Validate LLM response for safety. Returns JSON string."""
    try:
        logger.info(f"Validating response for query: {query[:60]}")
        # Use only the first chunk for response guardrail
        context_text = context_chunks[0].get("text", "") if context_chunks else ""
        result = engine.evaluate_response(query, context_text, response)
        logger.info(f"Response guardrail result: {result}")
        if isinstance(result, dict):
            if result.get("action") == "block":
                logger.warning(f"Response blocked: {result.get('reason')}")
                return json.dumps({
                    "valid": result.get("valid", False),
                    "grounded": result.get("grounded", False),
                    "issues": result.get("issues", [result.get("reason", "blocked")]),
                    "action": "block"
                })
            return json.dumps({"valid": True, "grounded": True, "issues": [], "action": "allow"})
        return json.dumps({"valid": False, "grounded": False, "issues": [str(result)], "action": "block"})
    except Exception as e:
        logger.error(f"Error in response_guardrail: {e}")
        return json.dumps({"valid": False, "grounded": False, "issues": [str(e)], "action": "block"})
