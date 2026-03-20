"""
This module defines the mcp tools for the document manager service
It provides tools for adding and deleting documents using the document manager service
"""
from fastmcp import FastMCP
from backend.logging_config import get_logger


logger = get_logger(__name__)
mcp=FastMCP("Org Knowledge MCP server")

@mcp.tool()
def add_org_document(org_id:str,document:str,metadata:dict={}):
    """
    Add a document to the org's vector store
    Args:
        org_id (str): The org's id
        document (str): The document to add
        metadata (dict): The metadata to add
    Returns:
        str: The document id or error message if failed
    """
    logger.info(f"Inside mcp tool of adding documents")
    from backend.knowledge_database.add_document import add_document_embeddings
    return add_document_embeddings(org_id, document, metadata)


@mcp.tool()
def del_org_document(org_id:str, document_id:str):
    """
    Delete a document from the org's vector store
    Args:
        org_id (str): The org's id
        document_id (str): The document id to delete
    Returns:
        str: Success message or error message if failed
    """
    logger.info(f"Inside mcp tool of deleting documents")
    from backend.knowledge_database.delete_document import delete_document_embeddings
    return delete_document_embeddings(org_id, document_id)


if __name__ == "__main__":
    mcp.run(transport="streamable-http",host="localhost", port=8001)
