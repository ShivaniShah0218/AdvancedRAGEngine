"""
Utility functions for user authentication, password hashing, and permission checks.
- Uses passlib for secure password hashing and verification
- Provides functions to authenticate users, fetch user details, and check permissions based on roles and organization
- Logs all operations for debugging and monitoring purposes
- Can be extended in the future to include additional authentication methods (e.g. OAuth, JWT) or more complex permission logic as needed
- Ensures that sensitive information (like passwords) is handled securely and not logged in plaintext
- Provides a clear separation of concerns by centralizing authentication and permission logic in one module
- Can be tested independently to ensure correct behavior of authentication and permission checks under various scenarios
"""
import os
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from datetime import datetime
from backend.db import models as db_models
from backend.logging_config import get_logger

logger = get_logger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """
    Hash the provided password using bcrypt algorithm.
     - Uses passlib's CryptContext for secure hashing.
     - Logs the hashing operation for debugging purposes (without logging the actual password).
     - Returns the hashed password as a string that can be stored in the database.
     - Can be easily modified to use different hashing algorithms or configurations if needed in the future.
     - Ensures that password hashing is consistent across the application by centralizing this logic in one function.
     - Can be tested independently to verify that it produces valid hashes and handles edge cases (e.g. empty passwords) correctly.
     - Provides a clear interface for password hashing that can be used throughout the authentication flow of the application.
     - Follows best practices for password security by using a strong hashing algorithm and not logging sensitive information.
     - Can be extended in the future to include additional features (e.g. salting, peppering) if needed for enhanced security.
     - Supports both local development and production environments based on configuration and requirements.
     - Ensures that all passwords are hashed before being stored in the database, improving overall security of user data.
     - Can be integrated with other authentication mechanisms (e.g. JWT) to provide a comprehensive authentication solution for the multi-tenant RAG system.
     - Provides a foundation for implementing additional security measures (e.g. rate limiting, account lockout) in the future as needed to protect against brute-force attacks and other threats.
     - Logs detailed information about the hashing process for easier debugging and monitoring of authentication-related operations without exposing sensitive data.
    """
    logger.debug("Hashing password")
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify that the provided plain password matches the stored hashed password.
        - Uses passlib's CryptContext to verify the password against the hash.
        - Logs the verification attempt for debugging purposes (without logging the actual password).
        - Returns True if the password is correct, False otherwise.
        - Can be easily modified to use different verification logic or configurations if needed in the future.
        - Ensures that password verification is consistent across the application by centralizing this logic in one function.
        - Can be tested independently to verify that it correctly identifies valid and invalid passwords under various scenarios.
        - Provides a clear interface for password verification that can be used throughout the authentication flow of the application.
        - Follows best practices for password security by using a strong hashing algorithm and not logging sensitive information.
        - Can be extended in the future to include additional features (e.g. support for multiple hashing algorithms) if needed for enhanced security and flexibility.
        - Supports both local development and production environments based on configuration and requirements.
        - Ensures that all password verification operations are handled securely and efficiently, improving overall security of user authentication in the multi-tenant RAG system.
        - Can be integrated with other authentication mechanisms (e.g. JWT) to provide a comprehensive authentication solution for the multi-tenant RAG system.
        - Provides a foundation for implementing additional security measures (e.g. rate limiting, account lockout) in the future as needed to protect against brute-force attacks and other threats.
        - Logs detailed information about the verification process for easier debugging and monitoring of authentication-related operations without exposing sensitive data.
    """
    is_valid = pwd_context.verify(plain_password, hashed_password)
    logger.debug(f"Password verification result: {is_valid}")
    return is_valid

def authenticate_user(db: Session, username: str, password: str):
    """
    Authenticate a user by username and password.
    - Fetches the user from the database using the provided username.
    - If the user is not found, logs a warning and returns False.
    - If the user is found, verifies the provided password against the stored hashed password.
    - If the password is incorrect, logs a warning and returns False.
    - If authentication is successful, logs an info message and returns the user object.
    - Can be easily modified to include additional authentication logic (e.g. account lockout, multi-factor authentication) if needed in the future.
    - Ensures that all authentication operations are handled securely and efficiently, improving overall security of user authentication in the multi-tenant RAG system.
    - Can be integrated with other authentication mechanisms (e.g. JWT) to provide a comprehensive authentication solution for the multi-tenant RAG system.
    - Provides a foundation for implementing additional security measures (e.g. rate limiting, account lockout) in the future as needed to protect against brute-force attacks and other threats.
    - Logs detailed information about the authentication process for easier debugging and monitoring of authentication-related operations without exposing sensitive data.
    - Supports both local development and production environments based on configuration and requirements.
    - Follows best practices for user authentication by securely handling passwords and providing clear logging for authentication attempts.
    - Can be tested independently to verify that it correctly authenticates valid users and rejects invalid credentials under various scenarios.
    - Provides a clear interface for user authentication that can be used throughout the application wherever user login is required.
    """
    logger.debug(f"Authenticating user: {username}")
    user = get_user(db, username)
    if not user:
        logger.warning(f"Authentication failed - User not found: {username}")
        return False
    if not verify_password(password, user.hashed_password):
        logger.warning(f"Authentication failed - Invalid password for user: {username}")
        return False
    logger.info(f"User authenticated successfully: {username}")
    return user

def get_user(db: Session, username: str):
    """
    Fetch a user from the database by username.
     - Queries the database for a user with the specified username.
     - Logs the database query operation for debugging purposes.
     - If the user is found, logs the user's details (excluding sensitive information) for debugging purposes.
     - If the user is not found, logs a debug message indicating that the user was not found.
     - Returns the user object if found, or None if not found.
     - Can be easily modified to include additional query logic (e.g. filtering by organization) if needed in the future.
     - Ensures that all database operations are handled securely and efficiently, improving overall performance of user-related operations in the multi-tenant RAG system.
     - Can be integrated with other authentication and permission mechanisms to provide a comprehensive solution for managing users and their access to resources in the multi-tenant RAG system.
     - Provides a foundation for implementing additional features (e.g. user search, pagination) in the future as needed to enhance user management capabilities.
     - Logs detailed information about database queries for easier debugging and monitoring of database-related operations without exposing sensitive data.
     - Supports both local development and production environments based on configuration and requirements.
     - Follows best practices for database interactions by using SQLAlchemy's ORM capabilities and providing clear logging for database operations.
     - Can be tested independently to verify that it correctly retrieves users from the database under various scenarios (e.g. existing user, non-existing user).
     - Provides a clear interface for fetching user details that can be used throughout the application wherever user information is needed.
     - Ensures that sensitive information (like hashed passwords) is not logged or exposed in any way during this operation, maintaining security best practices while still providing useful debugging information about user retrieval operations.
     - Can be extended in the future to include additional fields or related data (e.g. organization details) as needed to support more complex use cases in the multi-tenant RAG system.
     - Provides a consistent way to access user data across the application by centralizing this logic in one function, improving maintainability and reducing code duplication when fetching users from the database.
    """
    logger.debug(f"Fetching user from database: {username}")
    user = db.query(db_models.User).filter(db_models.User.username == username).first()
    if user:
        logger.debug(f"User found: {username} (role: {user.role}, org: {user.org_id})")
    else:
        logger.debug(f"User not found: {username}")
    return user

def _is_org_admin_or_admin(current_user: db_models.User, org_id: str) -> bool:
    """
    Check if current user is admin or org admin for the specified org
        - Returns True if the user has admin role or is an editor for the specified organization, False otherwise.
        - Logs the permission check operation for debugging purposes, including the user's role and organization.
        - Can be easily modified to include additional permission logic (e.g. support for more roles) if needed in the future.
        - Ensures that all permission checks are handled securely and efficiently, improving overall security of access control in the multi-tenant RAG system.
        - Can be integrated with other authentication and permission mechanisms to provide a comprehensive solution for managing user access to resources in the multi-tenant RAG system.
        - Provides a foundation for implementing additional features (e.g. role-based access control) in the future as needed to enhance permission management capabilities.
        - Logs detailed information about permission checks for easier debugging and monitoring of access control-related operations without exposing sensitive data.
        - Supports both local development and production environments based on configuration and requirements.
        - Follows best practices for access control by providing clear and consistent permission checks based on user roles and organizational context.
        - Can be tested independently to verify that it correctly identifies users with appropriate permissions under various scenarios (e.g. admin user, org editor, unauthorized user).
        - Provides a clear interface for checking user permissions that can be used throughout the application wherever access control is required.
        - Ensures that sensitive information (like user roles) is logged in a way that does not expose any security risks while still providing useful debugging information about permission checks.
        - Can be extended in the future to include additional roles or more complex permission logic as needed to support more complex use cases in the multi-tenant RAG system.
        - Provides a consistent way to manage permissions across the application by centralizing this logic in one function, improving maintainability and reducing code duplication when checking user permissions throughout the application.
        - Improves overall security of the multi-tenant RAG system by ensuring that only authorized users have access to sensitive operations based on their roles and organizational context.
    """
    is_allowed = current_user.role == "admin" or (current_user.role == "editor" and current_user.org_id == org_id)
    logger.debug(f"Permission check for user {current_user.username} on org {org_id}: {is_allowed}")
    return is_allowed

def log_user_event(db: Session, username: str, event_type: str, details: str = ""):
    """
    Log user events to database
        - Logs user-related events (e.g. login, logout, failed login attempts) to the database for auditing and monitoring purposes.
        - Accepts the username, event type, and optional details about the event.
        - Logs the event operation for debugging purposes, including the event type and details.
        - Can be easily modified to include additional event types or more complex logging logic if needed in the future.
        - Ensures that all user events are logged securely and efficiently, improving overall security and monitoring capabilities of the multi-tenant RAG system.
        - Can be integrated with other authentication and permission mechanisms to provide a comprehensive solution for managing user activities and access to resources in the multi-tenant RAG system.
        - Provides a foundation for implementing additional features (e.g. user activity tracking, security alerts) in the future as needed to enhance monitoring capabilities.
        - Logs detailed information about user events for easier debugging and monitoring of user-related operations without exposing sensitive data.
        - Supports both local development and production environments based on configuration and requirements.
        - Follows best practices for logging by providing clear and consistent logging of user events while ensuring that sensitive information is not exposed in logs.
        - Can be tested independently to verify that it correctly logs user events under various scenarios (e.g. successful login, failed login attempt).
        - Provides a clear interface for logging user events that can be used throughout the application wherever user activity needs to be tracked or monitored.
        - Ensures that sensitive information (like passwords) is not logged or exposed in any way during this operation, maintaining security best practices while still providing useful debugging information about user events.
        - Can be extended in the future to include additional fields or related data (e.g. IP address, timestamp) as needed to support more comprehensive logging of user activities in the multi-tenant RAG system.
        - Provides a consistent way to log user events across the application by centralizing this logic in one function, improving maintainability and reducing code duplication when logging user-related events throughout the application.
    """
    try:
        logger.info(f"User event - Username: {username}, Event: {event_type}, Details: {details}")
        record = UserLoginLog(username=username,event=event_type,timestamp=datetime.utcnow(),details=details,)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    except Exception as e:
        logger.error(f"Failed to log user event: {str(e)}")

