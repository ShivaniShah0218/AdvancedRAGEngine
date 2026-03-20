"""
Create or fetch a ChromaDB collection for an organization
"""
import os
from .chroma_client import fetch_client
from backend.logging_config import get_logger


logger = get_logger(__name__)


def get_collection_name(org_id:str):
    """
    Get the collection name for the organization
    :param org_id: The organization ID
    :return: The collection name
    """
    try:
        collection_name=f"org_{org_id}_knowledge"
        logger.info(f"Collection name fetched")
        return collection_name
    except Exception as e:
        logger.error(f"Error fetching collection name: {str(e)}")
        raise e

def get_or_create_collection(org_id:str):
    """
    Get or create a collection for the organization
    :param org_id: The organization ID
    :return: The collection
    """
    try:
        logger.info(f"Fetching Chromadb Persistent client")
        client=fetch_client()
        logger.info(f"Chromadb Persistent client fetched")
        collection_name=get_collection_name(org_id)
        logger.info(f"Getting or creating collection: {collection_name}")
        collection=client.get_or_create_collection(name=collection_name)
        logger.info(f"Collection {collection_name} created/fetched successfully")
        return collection
    except Exception as e:
        logger.error(f"Error getting or creating collection: {str(e)}")
        raise e
