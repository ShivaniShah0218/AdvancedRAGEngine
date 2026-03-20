"""
 Download the sentence transformer model from Hugging Face and save it to the specified path
"""

import os
from huggingface_hub import snapshot_download
from dotenv import load_dotenv
from backend.logging_config import get_logger

load_dotenv()

logger = get_logger(__name__)


MODEL_PATH=os.getenv("EMBEDDINGS_MODEL_PATH","./models")

def download_model():
    """
    Download the sentence transformer model from Hugging Face and save it to the specified path
    
    """
    try:
        logger.info("Downloading model...")
        model_name = "sentence-transformers/all-MiniLM-L6-v2"
        local_dir = os.path.abspath(MODEL_PATH)

        path = snapshot_download(
            repo_id=model_name,
            local_dir=local_dir,
            local_dir_use_symlinks=False
        )

        logger.info(f"Model downloaded to: {path}")
    except Exception as e:
        logger.error(f"Error downloading model: {str(e)}")
        raise e
