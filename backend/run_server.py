"""
Run initialization then start the FastAPI app (uvicorn) and MCP servers.

Usage (from project root):
  python -m backend.run_server         # default host 0.0.0.0 port 8000
  python -m backend.run_server --reload
  python -m backend.run_server --host 127.0.0.1 --port 8001

MCP servers run on ports 8001 (document manager), 8002 (guardrails), and 8003 (RAG pipeline).
"""
import os
import sys
import argparse
import threading
import time
from pathlib import Path
from dotenv import load_dotenv

# Ensure project root is on sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Load .env from project root
ENV_FILE = ROOT / '.env'
load_dotenv(dotenv_path=ENV_FILE)

# NOW import logging config (after loading .env)
from backend.logging_config import get_logger
logger = get_logger(__name__)

import uvicorn

logger.info("="*70)
logger.info("Advanced RAG Engine - Multi-tenant System Starting")
logger.info("="*70)

# Log environment info
debug_mode = os.getenv("DEBUG", "false").lower() == "true"
database_url = os.getenv("DATABASE_URL", "sqlite:///./rag_user_auth.db")
api_host = os.getenv("API_HOST", "0.0.0.0")
api_port = int(os.getenv("API_PORT", 8000))
mcp_host = os.getenv("MCP_HOST", "localhost")
mcp_port = int(os.getenv("MCP_PORT", 8001))
guardrails_mcp_port = int(os.getenv("GUARDRAILS_MCP_PORT", 8002))
rag_mcp_port = int(os.getenv("RAG_MCP_PORT", 8003))

logger.info(f"Environment: Debug={debug_mode}, Database={database_url}")
logger.info(f"Project root: {ROOT}")
logger.info(f"Env file: {ENV_FILE}")


def ensure_initialization():
    """
    Run database initialization
        - Creates tables if they don't exist
        - Ensures initial admin user is created
        - Logs all steps and handles exceptions gracefully
        - Can be extended to include other initialization tasks as needed
        - Provides a clear entry point for any setup logic that needs to run before the server starts accepting requests
        - Ensures that the application is in a ready state with necessary configurations and default data before handling API calls
        - Can be tested independently to verify that initialization logic works correctly under various scenarios (e.g. existing admin user, database errors)
    """
    logger.info("Starting application initialization...")
    try:
        import backend.db.init_config as init_config
        logger.debug("Database initialization module imported")
        
        if hasattr(init_config, "_ensure_initial_admin"):
            logger.info("Ensuring initial admin user exists...")
            init_config._ensure_initial_admin()
        
        logger.info("✅ Application initialization completed successfully")
    except Exception as e:
        logger.error(f"❌ Application initialization failed: {str(e)}", exc_info=True)
        raise


def start_mcp_server():
    """Start the document manager MCP server in a separate thread."""
    logger.info("Starting MCP server on http://localhost:8001...")
    try:
        from backend.knowledge_database.mcp_server import mcp
        mcp_thread = threading.Thread(
            target=mcp.run,
            kwargs={"transport": "streamable-http", "host": mcp_host, "port": mcp_port},
            daemon=True
        )
        mcp_thread.start()
        time.sleep(2)
        logger.info(f"✅ Document MCP server started on http://{mcp_host}:{mcp_port}")
        return mcp_thread
    except Exception as e:
        logger.error(f"❌ Failed to start document MCP server: {str(e)}", exc_info=True)
        return None


def start_guardrails_mcp_server():
    """Start the guardrails MCP server in a separate thread."""
    logger.info("Starting Guardrails MCP server on http://localhost:8002...")
    try:
        from backend.rag.guardrails.mcp_server import guardrails_mcp
        guardrails_thread = threading.Thread(
            target=guardrails_mcp.run,
            kwargs={"transport": "streamable-http", "host": mcp_host, "port": guardrails_mcp_port},
            daemon=True
        )
        guardrails_thread.start()
        time.sleep(2)
        logger.info(f"✅ Guardrails MCP server started on http://{mcp_host}:{guardrails_mcp_port}")
        return guardrails_thread
    except Exception as e:
        logger.error(f"❌ Failed to start guardrails MCP server: {str(e)}", exc_info=True)
        return None


def start_rag_mcp_server():
    """Start the RAG pipeline MCP server in a separate thread."""
    logger.info("Starting RAG MCP server on http://localhost:8003...")
    try:
        from backend.rag.mcp_server import rag_mcp
        rag_thread = threading.Thread(
            target=rag_mcp.run,
            kwargs={"transport": "streamable-http", "host": mcp_host, "port": rag_mcp_port},
            daemon=True
        )
        rag_thread.start()
        time.sleep(2)
        logger.info(f"✅ RAG MCP server started on http://{mcp_host}:{rag_mcp_port}")
        return rag_thread
    except Exception as e:
        logger.error(f"❌ Failed to start RAG MCP server: {str(e)}", exc_info=True)
        return None


def main():
    """
    Main entry point for the server
        - Parses command line arguments for host, port, reload, and workers
        - Runs initialization logic to set up database and default admin user
        - Starts the MCP server in a separate thread
        - Starts the uvicorn server with the specified configuration
        - Logs important information about the server status and configuration for monitoring and debugging purposes
        - Handles graceful shutdown on keyboard interrupt and logs any exceptions that occur during server startup
        - Provides clear instructions in the logs about where to access the API, documentation, metrics, and logs for easier monitoring and usage of the system
        - Can be extended to include additional command line options or initialization steps as needed in the future
        - Ensures that the server is started in a consistent and controlled manner, with proper logging and error handling throughout the process
        - Supports both local development (with auto-reload) and production deployment (with multiple workers) based on command line arguments
        - Provides a clear separation of concerns by encapsulating server startup logic in one function, making it easier to maintain and extend as the application evolves
        - Can be tested independently to verify that server startup behaves correctly under various configurations and scenarios (e.g. invalid host/port, database initialization errors)
        - Ensures that sensitive information (like database URLs) is not logged in plaintext while still providing enough context for debugging purposes.
        - Logs detailed information about the server configuration and status to help with monitoring and troubleshooting in production environments.
        - Provides a solid foundation for building out additional features or services that may need to run alongside the FastAPI server in the future (e.g. background tasks, scheduled jobs).
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Run the FastAPI server"
    )
    parser.add_argument(
        "--host",
        default=api_host,
        help=f"Host to bind to (default: {api_host})"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=api_port,
        help=f"Port to bind to (default: {api_port})"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload on code changes"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes (default: 1)"
    )
    
    args = parser.parse_args()
    
    logger.info(f"Server configuration: Host={args.host}, Port={args.port}, Reload={args.reload}, Workers={args.workers}")
    
    # Run initialization
    ensure_initialization()

    logger.info("Loading ensure_model function")
    from backend.utils.model_download_check import ensure_model
    # Check for embedding models download
    logger.info(f"Checking for embeddings model")
    EMBEDDINGS_MODEL_PATH=os.getenv("EMBEDDINGS_MODEL_PATH","./models")
    EMBEDDINGS_MODEL=os.getenv("EMBEDDINGS_MODEL")
    ensure_model(EMBEDDINGS_MODEL_PATH,EMBEDDINGS_MODEL)
    logger.info(f"Embeddings model {EMBEDDINGS_MODEL} download checked")

    #  Check for RAG models download
    logger.info(f"Checking for rag model")
    RAG_MODEL_PATH=os.getenv("RAG_MODEL_PATH","./models")
    RAG_MODEL=os.getenv("RAG_MODEL")
    ensure_model(RAG_MODEL_PATH,RAG_MODEL)
    logger.info(f"RAG model {RAG_MODEL} download checked")

    #  Check for cross encoder models download
    logger.info(f"Checking for cross encoder model")
    CROSS_ENCODER_MODEL_PATH=os.getenv("CROSS_ENCODER_MODEL_PATH","./models")
    CROSS_ENCODER_MODEL=os.getenv("CROSS_ENCODER_MODEL")
    ensure_model(CROSS_ENCODER_MODEL_PATH,CROSS_ENCODER_MODEL)
    logger.info(f"Cross Encoder model {CROSS_ENCODER_MODEL} download checked")

    #  Check for guardrails models download
    logger.info(f"Checking for guardrail model")
    GUARDRAILS_MODEL_PATH=os.getenv("GUARDRAILS_MODEL_PATH","./models")
    GUARDRAILS_MODEL=os.getenv("GUARDRAILS_MODEL")
    ensure_model(GUARDRAILS_MODEL_PATH,GUARDRAILS_MODEL)
    logger.info(f"Guardrail model {GUARDRAILS_MODEL} download checked")

    # Check for chromadb persistent storage directory created
    logger.info(f"Checking for Chromadb persistent directory")
    from backend.knowledge_database.chroma_client import initialize_kb_storage
    initialize_kb_storage()    
    logger.info(f"Chromadb persistent directory checked")

    # Start MCP servers
    mcp_thread = start_mcp_server()
    guardrails_thread = start_guardrails_mcp_server()
    rag_thread = start_rag_mcp_server()

    logger.info("All pre-start checks passed")
    # Start uvicorn server
    logger.info("Starting Uvicorn server...")
    logger.info(f"📍 API available at: http://{args.host}:{args.port}")
    logger.info(f"📖 Documentation: http://{args.host}:{args.port}/docs")
    logger.info(f"📊 Metrics: http://{args.host}:{args.port}/metrics")
    logger.info(f"📁 Logs directory: {Path(__file__).parent / 'logs'}")
    
    if mcp_thread:
        logger.info(f" Document MCP server running on http://{mcp_host}:{mcp_port}")
    if guardrails_thread:
        logger.info(f" Guardrails MCP server running on http://{mcp_host}:{guardrails_mcp_port}")
    if rag_thread:
        logger.info(f" RAG MCP server running on http://{mcp_host}:{rag_mcp_port}")
    
    logger.info("")
    logger.info("To start the Celery worker, run in a separate terminal:")
    logger.info("  celery -A backend.worker.celery_worker.celery_app worker -Q ingestion_queue --loglevel=info --pool=threads --concurrency=4")
    logger.info("")
    logger.info("MCP servers:")
    logger.info(f"  Document Manager: http://{mcp_host}:{mcp_port}")
    logger.info(f"  Guardrails: http://{mcp_host}:{guardrails_mcp_port}")
    logger.info(f"  RAG Pipeline: http://{mcp_host}:{rag_mcp_port}")
    logger.info("")
    
    try:
        uvicorn.run(
            "backend.app.app:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            workers=args.workers,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("Server shutdown initiated by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
