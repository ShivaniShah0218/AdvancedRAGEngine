"""
Function to create sentence embeddings for the text
- Uses SentenceTransformer model
- Returns embedding vectors

- Input: text (string or list of strings)
- Output: embedding vectors (list of lists)
- Example: create_embedding("This is a test sentence.")
    Output: [[0.123456789, 0.987654321, ...]]
"""
import os
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from backend.logging_config import get_logger



load_dotenv()

logger = get_logger(__name__)


MODEL_PATH=os.getenv("EMBEDDINGS_MODEL_PATH","sentence-transformers/all-MiniLM-L6-v2")

logger.info(f"Loading SentenceTransformer model from {MODEL_PATH}")
model=SentenceTransformer(MODEL_PATH)
logger.info("Model loaded successfully")

def create_embedding(text):
    """
    Create embedding vectors for the given text
    - Uses SentenceTransformer model to create embedding vectors
    """
    try:
        logger.info("Creating embedding for the given text")
        if isinstance(text, list):
            logger.info("Input is a list, encoding each element")
            return [model.encode(t).tolist() for t in text]
        logger.info("Input is a string, encoding the string")
        return model.encode(text).tolist()     
    except Exception as e:
        logger.error("Error creating embedding: %s", str(e))
        raise e
