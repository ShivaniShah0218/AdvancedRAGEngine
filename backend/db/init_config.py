"""
Database initialization and default admin creation
- Creates database tables if they don't exist
- Ensures an initial admin user is created based on environment variables
- Idempotent and safe to run multiple times without creating duplicates
- Logs all steps for debugging and monitoring purposes
- Uses SQLAlchemy for database management and session handling
- Loads configuration from .env file for flexibility across environments
- Handles exceptions gracefully and logs errors with stack traces for easier troubleshooting
"""
from dotenv import load_dotenv
import os
from backend.db.utils import get_user, get_password_hash
from backend.db.database_config import SessionLocal, Base, engine
from backend.db.models import User
from backend.logging_config import get_logger

logger = get_logger(__name__)

load_dotenv()

logger.info("Starting database initialization")

# Create tables
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified successfully")
except Exception as e:
    logger.error(f"Failed to create database tables: {str(e)}", exc_info=True)
    raise

INITIAL_ADMIN_USERNAME = os.getenv("INITIAL_ADMIN_USERNAME", "admin")
INITIAL_ADMIN_PASSWORD = os.getenv("INITIAL_ADMIN_PASSWORD", None)

logger.debug(f"Initial admin configuration - Username: {INITIAL_ADMIN_USERNAME}, Password set: {INITIAL_ADMIN_PASSWORD is not None}")

def _ensure_initial_admin():
    """
    Ensure the initial admin user exists in the database.
    This function is idempotent and safe to call multiple times.
        - Checks if a user with the specified username already exists.
        - If not, creates a new admin user with the provided password.
        - Logs all steps and handles exceptions gracefully.
        - Uses a database session to interact with the database and ensures it is properly closed after use.
        - Raises an error if there is an issue during user creation, which can be caught by the caller for further handling.
        - Can be extended in the future to include additional checks (e.g. password strength) or to create multiple default users if needed.
        - Provides a clear separation of concerns by encapsulating the admin user creation logic in one function.
        - Ensures that the application has at least one admin user for initial access and management.
        - Can be easily modified to support different default users or roles based on configuration.
        - Follows best practices for database interactions and error handling in Python applications.
        - Logs detailed information about the process for easier debugging and monitoring of the initialization process.
        - Can be tested independently to ensure it behaves correctly under various scenarios (e.g. existing user, database errors).
        - Provides a foundation for more complex initialization logic as the application evolves.
        - Ensures that sensitive information (like passwords) is handled securely and not logged in plaintext.
        - Can be integrated into a larger initialization routine that sets up other necessary components of the application as needed.
        - Supports both local development (with SQLite) and production environments (with other databases) based on configuration.
    """
    logger.info("Checking initial admin user...")
    
    if INITIAL_ADMIN_PASSWORD is None:
        logger.warning("INITIAL_ADMIN_PASSWORD not set in environment - skipping initial admin creation")
        return
    
    db = SessionLocal()
    try:
        admin = get_user(db, INITIAL_ADMIN_USERNAME)
        if admin is None:
            logger.info(f"Creating initial admin user: {INITIAL_ADMIN_USERNAME}")
            hashed_password = get_password_hash(INITIAL_ADMIN_PASSWORD)
            u = User(
                username=INITIAL_ADMIN_USERNAME,
                hashed_password=hashed_password,
                role="admin",
                org_id=None
            )
            db.add(u)
            db.commit()
            logger.info(f"Initial admin user created successfully: {INITIAL_ADMIN_USERNAME}")
        else:
            logger.info(f"Initial admin user already exists: {INITIAL_ADMIN_USERNAME}")
    except Exception as e:
        logger.error(f"Failed to create initial admin user: {str(e)}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()
        logger.debug("Database session closed")

# Auto-run on import
try:
    _ensure_initial_admin()
    logger.info("Database initialization completed successfully")
except Exception as e:
    logger.error(f"Database initialization failed: {str(e)}", exc_info=True)


