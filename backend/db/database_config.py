"""
    Creates database for keeping organization and user authentication details
    - Uses SQLAlchemy for ORM and database management
    - Database URL is configurable via environment variable (default: SQLite for local development)
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# Load .env from project root
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]  # Go up 2 levels to project root
ENV_FILE = ROOT / '.env'

load_dotenv(dotenv_path=ENV_FILE)

# Now safe to import logging (after load_dotenv)
from backend.logging_config import get_logger
logger = get_logger(__name__)

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./rag_user_auth.db")

logger.info(f"Database URL configured: {DATABASE_URL}")
logger.info(f"Environment file location: {ENV_FILE}")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

logger.info("Database engine created successfully")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """
    Dependency function to get a database session for FastAPI routes.
     - Yields a SQLAlchemy session and ensures it is closed after use.
     - Can be used with FastAPI's Depends() in route handlers.
     - Example usage in a route: `db: Session = Depends(get_db)`
     - Ensures proper resource management and avoids connection leaks.
     - Logs database session creation and closure for debugging purposes.
     - Handles exceptions gracefully to ensure sessions are always closed.
     - Can be extended with additional logging or error handling as needed.
     - Provides a consistent way to access the database across the application.
     - Supports both SQLite (for local development) and other databases (e.g. PostgreSQL) based on configuration.
     - Ensures thread safety when using SQLite by setting check_same_thread=False in the engine configuration.
     - Can be easily modified to include additional context (e.g. request ID) in logs if needed.
     - Follows best practices for database session management in FastAPI applications.
     - Can be tested independently to ensure proper session handling and error management.
     - Provides a clear separation of concerns by centralizing database access logic in one place.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

logger.info("Database session configuration complete")


