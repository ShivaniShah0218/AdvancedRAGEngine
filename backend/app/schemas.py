"""
Pydantic schemas for the API endpoints
"""
from pydantic import BaseModel, Field
from typing import Optional


class Token(BaseModel):
    """
    Schema for authentication token response
        - access_token: the JWT token string that clients will use for authenticated requests
        - token_type: typically "bearer" to indicate the type of token
        - role: the role of the authenticated user (e.g. "admin", "editor", "viewer") which can be used by clients to adjust UI/UX based on permissions
        Example response:
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer",
            "role": "admin"
        }
        This schema is used in the API endpoint for user login and ensures that the response data is properly structured and validated before being sent to the client.
        Clients can rely on this schema to know what fields to expect in the authentication response and how to use them for subsequent API calls.
        The role field allows clients to implement role-based access control on the frontend, adjusting available features based on the user's permissions.
        Overall, this schema plays a crucial role in the authentication flow of the multi-tenant RAG system.
        It ensures that authentication responses are consistent and contain all necessary information for clients to manage user sessions effectively.
        By validating the structure of the token response, we can prevent issues with malformed tokens and improve the security and reliability of the authentication process.
        The access_token should be treated securely by clients, as it grants access to protected resources in the API. It should be stored securely (e.g. in memory or secure storage) and included in the Authorization header of subsequent API requests.
        The token_type indicates how clients should use the access_token (e.g. as a Bearer token), which is important for ensuring proper authentication in API calls.
        The role field provides essential context about the user's permissions, allowing clients to implement appropriate access controls and UI adjustments based on user roles.
        In summary, this Token schema is a critical component of the authentication mechanism in our multi-tenant RAG system, providing a clear contract for how authentication responses should be structured and what information they should contain.
        It helps ensure that both the backend and frontend are aligned in terms of how authentication data is handled, improving security and usability across the system.
    """
    access_token: str
    token_type: str
    role: str

class OrgCreate(BaseModel):
    """
    Schema for creating a new organization
     - org_id: unique identifier for the organization (alphanumeric, underscores, hyphens)
     - org_name: optional human-readable name for the organization
     Validation:
     - org_id must match the regex pattern to ensure it is a valid identifier
     - org_name is optional and can be any string
     Example:
     {
         "org_id": "example_org",
         "org_name": "Example Organization"
     }
     This schema is used in the API endpoint for creating new organizations and ensures that the input data is properly validated before processing.
    """
    org_id: str = Field(...,pattern=r"^[A-Za-z0-9_\-]+$")
    org_name: Optional[str] = None

class UserCreate(BaseModel):
    """
    Schema for creating a new user
    - username: unique identifier for the user (alphanumeric, underscores, hyphens)
    - password: the user's password (should be securely handled and hashed before storage)
    - role: the user's role (must be one of "viewer", "editor", "admin")
    Validation:
    - username must match the regex pattern to ensure it is a valid identifier
    - role must be one of the specified values to ensure valid user roles
    
    """
    username: str = Field(...,pattern=r"^[A-Za-z0-9_\-]+$")
    password: str
    role: str = Field(...,pattern=r"^(viewer|editor|admin)$")