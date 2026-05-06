"""
 Check if the model exists, download if it doesn't

"""
import os
from dotenv import load_dotenv
from backend.logging_config import get_logger
from backend.utils.model_download import download_model

load_dotenv()

logger = get_logger(__name__)

# MODEL_PATH=os.getenv("EMBEDDINGS_MODEL_PATH")

def ensure_model(model_path,model_name):
    """
    Ensure the model exists, download if it doesn't
    """
    try:
        if not os.path.exists(model_path) or not os.listdir(model_path):
            logger.info(f"Downloading model {model_path}...")
            download_model(model_path,model_name)
        else:
            logger.info(f"Model {model_path} already exists")
    except Exception as e:
        logger.error(f"Error ensuring model: {str(e)}")
        raise
