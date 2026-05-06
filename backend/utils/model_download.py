"""
 Download the model from Hugging Face and save it to the specified path
"""

import os
from huggingface_hub import snapshot_download
from dotenv import load_dotenv
from backend.logging_config import get_logger

load_dotenv()

logger = get_logger(__name__)


# MODEL_PATH=os.getenv("EMBEDDINGS_MODEL_PATH","./models")

def download_model(model_path,model_name):
    """
    Download the sentence transformer model from Hugging Face and save it to the specified path
    
    """
    try:
        logger.info("Downloading model...")
        
        local_dir = os.path.abspath(model_path)

        path = snapshot_download(
            repo_id=model_name,
            local_dir=local_dir,
            local_dir_use_symlinks=False
        )

        logger.info(f"Model downloaded to: {path}")
    except Exception as e:
        logger.error(f"Error downloading model: {str(e)}")
        raise e
