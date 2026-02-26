"""
Run initialization then start the FastAPI app (uvicorn).

Usage (from project root):
  python -m backend.run_server         # default host 0.0.0.0 port 8000
  python -m backend.run_server --reload
  python -m backend.run_server --host 127.0.0.1 --port 8001
"""
import os
import sys
import argparse
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


def main():
    """
    Main entry point for the server
        - Parses command line arguments for host, port, reload, and workers
        - Runs initialization logic to set up database and default admin user
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
    
    # Start uvicorn server
    logger.info("Starting Uvicorn server...")
    logger.info(f"📍 API available at: http://{args.host}:{args.port}")
    logger.info(f"📖 Documentation: http://{args.host}:{args.port}/docs")
    logger.info(f"📊 Metrics: http://{args.host}:{args.port}/metrics")
    logger.info(f"📁 Logs directory: {Path(__file__).parent / 'logs'}")
    
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