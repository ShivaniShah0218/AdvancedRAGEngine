"""
Creates or Fetches collection for the organization based on org_id
Uses PersistentClient to store the data in the local filesystem

"""
import os
import chromadb
from dotenv import load_dotenv
from backend.logging_config import get_logger

load_dotenv()

logger = get_logger(__name__)

CHROMA_DIRECTORY = os.getenv("CHROMA_DIRECTORY", "./chroma_storage")
logger.info(f"CHROMA DIRECTORY: {CHROMA_DIRECTORY}")

def initialize_kb_storage():
    """
    Creates storage directory for the chroma vector database
    """
    try:
        logger.info(f"Creating chroma storage directory: {CHROMA_DIRECTORY}")
        os.makedirs(CHROMA_DIRECTORY, exist_ok=True)
        logger.info(f"Chroma storage directory ready: {CHROMA_DIRECTORY}")
        logger.info("Chroma storage directory created successfully")
    except Exception as e:
        logger.error(f"Error creating chroma storage directory: {e}")
        raise e


def fetch_client():
    """
    Creates Persistent Client to store vectors in the local filesystem
    """
    try:
        logger.info("Creating Chroma Client")
        client=chromadb.PersistentClient(path=CHROMA_DIRECTORY)
        logger.info("Created ChromaDB Client")
        return client
    except Exception as e:
        logger.error(f"Error creating chroma client: {e}")
        raise e


