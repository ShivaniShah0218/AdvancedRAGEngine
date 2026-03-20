"""
Creates chunks for the uploaded document
- Uses RecursiveCharacterTextSplitter to split the document into chunks of 1000 characters with 200 characters overlap
- Returns the chunks
- Logs the number of documents and chunks
"""
from langchain_text_splitters import RecursiveCharacterTextSplitter
from backend.logging_config import get_logger

logger = get_logger(__name__)

text_splitter=RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

def create_chunks(document):
    """
    Split the document into chunks
    :param document: document to be chunked
    :return: list of chunks
    """
    try:
        if len(document)>0:
            chunks=text_splitter.split_documents(document)
            logger.info(f"Loaded {len(document)} document, split into {len(chunks)} chunks.")
            return chunks
        else:
            logger.error("Empty document received for chunking")
            raise "Empty document received for chunking"           
    except Exception as e:
        logger.error(f"Error in creating chunks: {str(e)}")
        raise e

