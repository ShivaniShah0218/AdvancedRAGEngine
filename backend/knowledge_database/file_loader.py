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





# import os
# from langchain_community.document_loaders import PyPDFLoader, UnstructuredCSVLoader, UnstructuredExcelLoader, TextLoader, UnstructuredWordDocumentLoader
# from langchain_community.vectorstores import Chroma
# from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
# from langchain.text_splitter import RecursiveCharacterTextSplitter

# # 1. Define file loaders for each format
# def load_documents_from_directory(directory_path):
#     all_documents = []
#     for filename in os.listdir(directory_path):
#         file_path = os.path.join(directory_path, filename)
#         if filename.endswith(".pdf"):
#             loader = PyPDFLoader(file_path)
#         elif filename.endswith(".csv"):
#             # mode="single" loads the entire CSV as a single document; use other modes for row-by-row
#             loader = UnstructuredCSVLoader(file_path, mode="single")
#         elif filename.endswith(".xlsx") or filename.endswith(".xls"):
#             loader = UnstructuredExcelLoader(file_path, mode="single")
#         elif filename.endswith(".txt"):
#             loader = TextLoader(file_path)
#         elif filename.endswith(".docx") or filename.endswith(".doc"):
#             loader = UnstructuredWordDocumentLoader(file_path)
#         else:
#             continue # Skip unsupported files
        
#         all_documents.extend(loader.load())
#     return all_documents

# # 2. Load and split documents
# # Ensure you have a 'data_directory' with your files
# data_directory = "./your_data_folder" 
# documents = load_documents_from_directory(data_directory)

# # Split documents into chunks for better retrieval
# text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
# chunked_documents = text_splitter.split_documents(documents)
# print(f"Loaded {len(documents)} documents, split into {len(chunked_documents)} chunks.")

# # 3. Initialize Embedding Function
# # Using a local sentence transformer model for embeddings
# embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# # 4. Store in ChromaDB
# # This will create a local directory "chroma_storage" to persist the database
# persist_directory = "chroma_storage"
# vector_db = Chroma.from_documents(
#     documents=chunked_documents,
#     embedding=embedding_function,
#     persist_directory=persist_directory
# )

# # Persist the database to disk
# vector_db.persist()
# print(f"Documents stored successfully in ChromaDB at {persist_directory}.")

# # 5. Example Query (Optional)
# query = "What information is available about a specific topic?"
# results = vector_db.similarity_search(query, k=2)

# print("\nQuery Results:")
# for doc in results:
#     print(f"Source: {doc.metadata['source']}")
#     print(f"Content: {doc.page_content[:200]}...")
#     print("-" * 20)

