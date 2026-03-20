"""
  Contains models for the database tables creation
  - Uses SQLAlchemy ORM to define models for organizations, users, and user login logs
  - Organization model: stores organization authentication information (org_id, name, created_at)
  - User model: stores user authentication information (username, hashed_password, role, org_id, created_at)
  - UserLoginLog model: tracks user authentication-related events for auditing and monitoring (event, timestamp, details)
  - UserRole enum: defines possible user roles (admin, editor, viewer) for role-based access control
  - Relationships: Organization has many Users, User belongs to an Organization
  - Each model includes an __init__ method for easy instantiation and logging of model creation
  - The UserLoginLog model allows for detailed tracking of authentication events, which can be crucial for security auditing and monitoring user activity.
  - DocumentRecord model: tracks documents added to an organization's knowledge base (doc_id, org_id, filename, uploaded_by, uploaded_at, is_deleted, job_id, status, error_message)
  - KnowledgeBaseAuditLog model: records audit log entries for knowledge base actions (id, action, doc_id, org_id, performed_by, timestamp, details)
  
  """
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Integer, Enum as SQLEnum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
import enum

from backend.db.database_config import Base
from backend.logging_config import get_logger

logger = get_logger(__name__)

class UserRole(str, enum.Enum):
    """
    Enum for user roles in the system
     - ADMIN: has full access to all resources and management capabilities
     - EDITOR: can create and modify resources but may have limited access to management features
     - VIEWER: can only view resources and has no permissions to create or modify anything
     This enum is used in the User model to define the role of each user, which can then be used for role-based access control in the API endpoints.
     By defining user roles as an enum, we ensure that only valid roles can be assigned to users and make it easier to manage permissions based on these roles throughout the application.
     The use of string values for the enum allows for easier readability and debugging when inspecting user data in logs or database entries.
     This structure also allows for easy extension in the future if additional roles are needed (e.g. "org_admin" for organization-specific administrators) without requiring significant changes to the existing codebase.
     Overall, this UserRole enum is a critical component of the authentication and authorization system in our multi-tenant RAG application, providing a clear definition of user permissions and facilitating secure access control across the system.
    """
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

class Organization(Base):
    """
    Stores organization authentication information
        - org_id: unique identifier for the organization (primary key)
        - name: optional human-readable name for the organization
        - created_at: timestamp of when the organization was created
        - users: relationship to User model, indicating which users belong to this organization
        This model is used to manage organizations in the multi-tenant system, allowing us to associate users with specific organizations and implement organization-level access control.
        By defining a relationship between Organization and User, we can easily query which users belong to a given organization and enforce permissions based on organizational membership.
        The created_at field allows us to track when each organization was created, which can be useful for auditing and monitoring purposes.
        Overall, this Organization model is a fundamental part of the multi-tenant architecture, enabling us to manage multiple organizations and their associated users within a single application instance.
        It provides the necessary structure for implementing organization-specific features and access controls as needed in the future.
        The __init__ method includes logging to help track when new organizations are instantiated, which can be useful for debugging and monitoring the creation of new organizational entities in the system.
        This model can be extended in the future to include additional fields (e.g. contact information, subscription status) as needed without affecting the core functionality of user authentication and organization management.
        By keeping the model simple and focused on authentication-related information, we ensure that it remains flexible and adaptable to future requirements while still providing the necessary foundation for managing organizations in our multi-tenant RAG system.
        The use of SQLAlchemy's declarative base allows us to easily define our database schema through Python classes, making it straightforward to manage database interactions and migrations as our application evolves.
        Overall, this Organization model is designed to be a robust and flexible component of our multi-tenant architecture, providing essential functionality for managing organizations and their associated users while allowing for future growth and enhancements as needed.
        The logging included in the __init__ method helps provide visibility into when new organizations are created, which can be valuable for both debugging during development and monitoring in production environments.
    """
    __tablename__ = "organizations"
    org_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    users = relationship("User", back_populates="organization")
    
    def __init__(self, org_id, name):
        self.org_id = org_id
        self.name = name
        logger.debug(f"Organization model instantiated: {org_id}")

class User(Base):
    """
    Stores users authentication information
    - username: unique identifier for the user (primary key)
    - hashed_password: the user's password (should be securely handled and hashed before storage)
    - role: the user's role (must be one of "viewer", "editor", "admin")
    - org_id: foreign key to the organization the user belongs to (null for global admin)
    - created_at: timestamp of when the user was created
    - organization: relationship to the Organization model, indicating which organization the user belongs to
    This model is used to manage users in the multi-tenant system, allowing us to associate users with specific organizations and implement role-based access control based on their assigned roles.
    By defining a relationship between User and Organization, we can easily query which organization a user belongs to and enforce permissions based on both their role and organizational membership.
    The created_at field allows us to track when each user was created, which can be useful for auditing and monitoring purposes.
    The role field is critical for implementing role-based access control in the API endpoints, allowing us to differentiate between users with different levels of permissions (e.g. admin vs viewer) and enforce appropriate access controls based on their assigned roles.
    Overall, this User model is a fundamental part of the multi-tenant architecture, enabling us to manage multiple users and their associated organizations within a single application instance while providing the necessary structure for implementing role-based access control across the system.
    The __init__ method includes logging to help track when new users are instantiated, which can be useful for debugging and monitoring the creation of new user entities in the system.
    This model can be extended in the future to include additional fields (e.g. full name, email) as needed without affecting the core functionality of user authentication and organization management.
    By keeping the model focused on authentication-related information, we ensure that it remains flexible and adaptable to future requirements while still providing the necessary foundation for managing users in our multi-tenant RAG system.
    The use of SQLAlchemy's declarative base allows us to easily define our database schema through Python classes, making it straightforward to manage database interactions and migrations as our application evolves.
    """
    __tablename__ = "users"
    username = Column(String, primary_key=True, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole, values_callable=lambda x: [e.value for e in x]), default=UserRole.VIEWER.value)  # admin, org_admin, user
    org_id = Column(String, ForeignKey("organizations.org_id"))  # null for global admin
    created_at = Column(DateTime, default=datetime.utcnow)
    
    organization = relationship("Organization", back_populates="users")
    
    def __init__(self, username, hashed_password, role, org_id):
        self.username = username
        self.hashed_password = hashed_password
        self.role = role
        self.org_id = org_id
        logger.debug(f"User model instantiated: {username} (role: {role}, org: {org_id})")

class DocumentRecord(Base):
    """
    Tracks documents added to an organization's knowledge base.
    - doc_id: unique document identifier (UUID)
    - org_id: the organization this document belongs to
    - filename: original filename of the uploaded document
    - uploaded_by: username of the editor who uploaded it
    - uploaded_at: timestamp of upload
    - is_deleted: soft-delete flag
    """
    __tablename__ = "document_records"
    doc_id = Column(String, primary_key=True, index=True)
    org_id = Column(String, ForeignKey("organizations.org_id"), nullable=False, index=True)
    filename = Column(String, nullable=False)
    uploaded_by = Column(String, ForeignKey("users.username"), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
    # Celery job tracking
    job_id = Column(String, nullable=True, index=True)
    status = Column(String, default="pending")  # pending | processing | done | failed
    error_message = Column(Text, nullable=True)

    organization = relationship("Organization")
    uploader = relationship("User", foreign_keys=[uploaded_by])

    def __init__(self, doc_id, org_id, filename, uploaded_by, job_id=None):
        self.doc_id = doc_id
        self.org_id = org_id
        self.filename = filename
        self.uploaded_by = uploaded_by
        self.job_id = job_id
        self.status = "pending"
        logger.debug(f"DocumentRecord instantiated: {doc_id} for org {org_id}")


class KnowledgeBaseAuditLog(Base):
    """
    Audit log for knowledge base actions performed by editors.
    - action: 'document_added', 'document_deleted'
    - doc_id: the document involved
    - org_id: the organization
    - performed_by: username of the editor
    - timestamp: when the action occurred
    - details: optional extra context
    """
    __tablename__ = "kb_audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String, nullable=False, index=True)
    doc_id = Column(String, nullable=True)
    org_id = Column(String, nullable=False, index=True)
    performed_by = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    details = Column(Text, nullable=True)


class UserLoginLog(Base):
    """
    Tracks user authentication-related events for auditing and monitoring.
    - event: 'login_success', 'login_failure', 'logout', 'token_refresh', etc.
    - timestamp: UTC time of the event
    - details: free-text JSON or string for additional context (e.g. failure reason)
    This model is used to log authentication events related to users, providing valuable information for security auditing and monitoring user activity within the multi-tenant system.
    By tracking events such as successful logins, failed login attempts, logouts, and token refreshes, we can gain insights into user behavior and identify potential security issues (e.g. multiple failed login attempts indicating a brute-force attack).
    The details field allows us to store additional context about each event, such as the reason for a login failure or the source IP address of a login attempt, which can be crucial for investigating security incidents and improving the overall security posture of the application.
    Overall, this UserLoginLog model is an important component of our multi-tenant architecture, providing essential functionality for tracking authentication events and enhancing the security monitoring capabilities of our RAG system.
    The use of SQLAlchemy's declarative base allows us to easily define our database schema through Python classes, making it straightforward to manage database interactions and migrations as our application evolves.
    This model can be extended in the future to include additional fields (e.g. user agent, source IP) as needed without affecting the core functionality of logging authentication events.
    By keeping the model focused on authentication-related events, we ensure that it remains flexible and adaptable to future requirements while still providing the necessary foundation for tracking user activity in our multi-tenant RAG system.
    The logging included in the __init__ method helps provide visibility into when new log entries are created, which can be valuable for both debugging during development and monitoring in production environments.
    Overall, this UserLoginLog model is designed to be a robust and flexible component of our multi-tenant architecture, providing essential functionality for tracking authentication events and enhancing the security monitoring capabilities of our RAG system.
    It allows us to maintain a detailed record of user authentication activity, which can be crucial for identifying potential security issues and improving the overall security posture of our application.
    """
    __tablename__ = "user_login_logs"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True, nullable=True)
    event = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    details = Column(Text, nullable=True)


