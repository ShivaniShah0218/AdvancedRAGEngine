"""
 Check if the sentence embedding model exists, download if it doesn't

"""
import os
from dotenv import load_dotenv
from backend.logging_config import get_logger
from .model_download import download_model

load_dotenv()

logger = get_logger(__name__)

MODEL_PATH=os.getenv("EMBEDDINGS_MODEL_PATH")

def ensure_model():
    """
    Ensure the model exists, download if it doesn't
    """
    try:
        if not os.path.exists(MODEL_PATH) or not os.listdir(MODEL_PATH):
            logger.info(f"Downloading model {MODEL_PATH}...")
            download_model()
        else:
            logger.info(f"Model {MODEL_PATH} already exists")
    except Exception as e:
        logger.error(f"Error ensuring model: {str(e)}")
        raise
