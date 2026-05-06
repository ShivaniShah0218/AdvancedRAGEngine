"""
 Defines file loader for creating embeddings and storing in vector database.
 Supported formats: PDF, TXT, DOC, DOCX, CSV, XLSX, XLS
"""
from langchain_community.document_loaders import PyPDFLoader,UnstructuredCSVLoader,UnstructuredExcelLoader,UnstructuredWordDocumentLoader, TextLoader
from backend.logging_config import get_logger

logger = get_logger(__name__)


def load_document(filename):
    """
    Load a document based on its file extension.

    Args:
        filename (str): The path to the file to be loaded.

    Returns:
        List[Document]: A list of Document objects if successful, None otherwise.

    """
    logger.info(f"Loading file: {filename}")
    try:
        if filename.endswith(".pdf"):
            loader=PyPDFLoader(filename)
            logger.info(f"File {filename} loaded")
            return loader.load()
        elif filename.endswith(".txt"):
            loader=TextLoader(filename)
            logger.info(f"File {filename} loaded")
            return loader.load()
        elif filename.endswith(".doc") or filename.endswith(".docx"):
            loader=UnstructuredWordDocumentLoader(filename)
            logger.info(f"File {filename} loaded")
            return loader.load()
        elif filename.endswith(".csv"):
            loader=UnstructuredCSVLoader(filename,mode="single")
            logger.info(f"File {filename} loaded")
            return loader.load()
        elif filename.endswith(".xlsx") or filename.endswith(".xls"):
            loader=UnstructuredExcelLoader(filename,mode="single")
            logger.info(f"File {filename} loaded")
            return loader.load()
        else:
            loader=None
            logger.info(f"Unsupported file formats for file {filename}")        
            return None
    except Exception as e:
        logger.error(f"Error loading file {filename}: {str(e)}")
        return None



