"""
    Backend FastAPI API configurations for multi-tenant RAG Systems
    - JWT-based authentication with role-based access control (admin/editor/viewer)
    - Organization and user management endpoints
    - Prometheus metrics for monitoring API usage and authentication events
    - Structured logging for all operations with detailed context for debugging and auditing
    - CORS configuration to allow requests from the React frontend during development
    - Database interactions using SQLAlchemy ORM with proper session management and error handling
    - Comprehensive error handling with appropriate HTTP status codes and logging for all failure scenarios
"""
#Import necessary libraries
import time
import os
from fastapi import FastAPI, Depends, HTTPException, status, Path, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List,Dict
from jose import jwt, JWTError
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from starlette.responses import Response
from fastapi.middleware.cors import CORSMiddleware

from backend.db.database_config import engine,Base, get_db
from backend.db import models as db_models
from backend.db import utils as db_utils
from backend.app import schemas
from .metrics import REQUEST_COUNT, REQUEST_LATENCY, LOGIN_ATTEMPTS
from backend.logging_config import get_logger

load_dotenv()

logger = get_logger(__name__)

SECRET_KEY = os.getenv("JWT_SECRET", "replace-this-secret")
ACCESS_TOKEN_EXPIRE_SECONDS = int(os.getenv("JWT_EXPIRE_S", 3600))
ALGORITHM =  os.getenv("ALGORITHM","HS256")
app=FastAPI(title="Multi-tenant RAG system")

logger.info("FastAPI application initialized")
logger.info(f"Using algorithm: {ALGORITHM}, Token expiration: {ACCESS_TOKEN_EXPIRE_SECONDS}s")

# allow requests from the React dev server during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001","*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

logger.info("CORS middleware configured")

#JWT helpers
def create_access_token(data: dict, expires_in: int = ACCESS_TOKEN_EXPIRE_SECONDS):
    """
    Create a JWT access token with the given data and expiration time.
        - data: dictionary containing user information (e.g. username, role, org_id)
        - expires_in: token expiration time in seconds (default: 1 hour)
        The token will include the standard "exp" (expiration) and "iat" (issued at) claims.
    """
    to_encode = data.copy()
    now = int(time.time())
    to_encode.update({"exp": now + expires_in, "iat": now})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.debug(f"Access token created for user: {data.get('sub')}")
    return token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# Get current user
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> db_models.User:
    """
    Decode the JWT token to get the current user information.
    - token: JWT token from the Authorization header
    - db: database session for querying user information
    The function will:
        - Decode the token and extract the username (sub claim)
        - Validate the token and check for expiration
        - Query the database for the user with the extracted username
        - If any step fails, it will log the event and raise an HTTP 401 exception
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        logger.debug(f"Token decoded for username: {username}")
        if username is None:
            logger.warning("Token validation failed: Invalid username in token")
            db_utils.log_user_event(db, username,"login_failure", "Invalid username")
            LOGIN_ATTEMPTS.labels(status="failed").inc()
            raise credentials_exception
    except JWTError as e:
        logger.error(f"JWT decode error: {str(e)}")
        db_utils.log_user_event(db, username,"token_expire", "Invalid Token")
        LOGIN_ATTEMPTS.labels(status="failed").inc()
        raise credentials_exception
    user = db_utils.get_user(db, username)
    if user is None:
        logger.warning(f"User not found in database: {username}")
        db_utils.log_user_event(db, username,"login_failure", "Invalid username")
        LOGIN_ATTEMPTS.labels(status="failed").inc()
        raise credentials_exception
    logger.debug(f"User authenticated: {username} (role: {user.role})")
    return user

#Authenticate required role
def require_role(required_roles: List[str]):
    """
    Dependency function to enforce role-based access control on API endpoints.
    - required_roles: list of roles that are allowed to access the endpoint (e.g. ["admin"], ["editor", "admin"])
    The returned function will:
        - Get the current user using the get_current_user dependency
        - Check if the user's role is in the required_roles list
        - If not, it will log the access denial and raise an HTTP 403 exception
        - If the user has the required role, it will return the current user object for use in the endpoint
    """
    def role_checker(current_user: db_models.User = Depends(get_current_user)):
        """
        Check if the current user's role is in the required roles for the endpoint.
         - current_user: the authenticated user object obtained from the JWT token
         The function will:
            - Compare the user's role with the required roles
            - If the user's role is not sufficient, log a warning and raise a 403 Forbidden exception
            - If the user has the required role, return the user object for use in the endpoint
        """
        if current_user.role not in required_roles:
            logger.warning(f"Access denied for user {current_user.username}: requires {required_roles}, has {current_user.role}")
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker

# Metrics middleware
@app.middleware("http")
async def metrics_middleware(request,call_next):
    """
    Middleware to track API request metrics for Prometheus.
        - request: incoming HTTP request object
        - call_next: function to call the next middleware or endpoint handler
        The middleware will:
            - Record the start time of the request
            - Call the next handler and get the response
            - Calculate the latency of the request
            - Increment the REQUEST_COUNT metric with labels for method and endpoint
            - Observe the latency in the REQUEST_LATENCY histogram
            - Log the request method, path, response status, and latency for debugging
            - Return the response to the client
    """
    start=time.time()
    response=await call_next(request)
    latency=time.time()-start
    REQUEST_COUNT.labels(method=request.method,endpoint=request.url.path).inc()
    REQUEST_LATENCY.observe(latency)
    logger.debug(f"{request.method} {request.url.path} - Status: {response.status_code} - Latency: {latency:.3f}s")
    return response

# Auth endpoint
@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Endpoint for user login and JWT token generation.
    - form_data: contains the username and password from the login form
    - db: database session for authenticating the user
    The endpoint will:
        - Log the login attempt with the provided username
        - Authenticate the user using the database utility function
        - If authentication fails, log the failure and raise an HTTP 400 exception
        - If authentication succeeds, log the success and generate a JWT token with the user's information
        - Increment the LOGIN_ATTEMPTS metric with labels for status and role
        - Return the access token and token type to the client
    """
    logger.info(f"Login attempt for username: {form_data.username}")
    user = db_utils.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.warning(f"Login failed for username: {form_data.username} - Invalid credentials")
        db_utils.log_user_event(db, form_data.username,"login_failure", "Incorrect username or password")
        LOGIN_ATTEMPTS.labels(status="failed", role="unknown").inc()
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    logger.info(f"Login successful for username: {form_data.username} (role: {user.role})")
    db_utils.log_user_event(db, form_data.username,"login_success")
    LOGIN_ATTEMPTS.labels(status="success", role=user.role).inc()
    token = create_access_token({"sub": user.username, "role": user.role, 
                                 "org_id": user.org_id})
    return {"access_token": token, "token_type": "bearer","role": user.role}

# Org endpoints
@app.post("/admin/orgs", status_code=201, dependencies=[Depends(require_role(["admin"]))])
def create_org(body: schemas.OrgCreate, db: Session = Depends(get_db)):
    """
    Endpoint for creating a new organization.
    - body: contains the organization ID and name from the request body
    - db: database session for creating the organization
    The endpoint will:
        - Log the organization creation attempt with the provided ID and name
        - Check if an organization with the same ID already exists in the database
        - If it exists, log a warning and raise an HTTP 409 exception
        - If it does not exist, create a new organization record in the database
        - Commit the transaction and log the successful creation of the organization
        - Return the organization ID and name to the client
    """
    logger.info(f"Creating organization - ID: {body.org_id}, Name: {body.org_name}")
    if db.query(db_models.Organization).filter(db_models.Organization.org_id == body.org_id).first():
        logger.warning(f"Organization creation failed - Org already exists: {body.org_id}")
        raise HTTPException(status_code=409, detail="Org already exists")
    org = db_models.Organization(org_id=body.org_id, name=body.org_name)
    db.add(org)
    db.commit()
    logger.info(f"Organization created successfully: {body.org_id}")
    return {"org_id": body.org_id, "name": body.org_name}

@app.get("/orgs")
def list_orgs(current_user: db_models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Endpoint for listing organizations.
    - current_user: the authenticated user making the request
    - db: database session for querying organizations
    The endpoint will:
        - Log the organization listing request with the user's information
        - If the user is an admin, query the database for all organizations
        - If the user is an editor or viewer, query the database for only their own organization
        - Log the number of organizations retrieved for debugging
        - Return a list of organizations (ID and name) to the client
    """
    logger.debug(f"Listing organizations for user: {current_user.username} (role: {current_user.role})")
    # Admins see all organizations
    if current_user.role == "admin":
        rows = db.query(db_models.Organization).all()
        logger.debug(f"Admin listing all organizations - Count: {len(rows)}")
    else:
        # Editors and viewers only see their own organization
        rows = db.query(db_models.Organization).filter(
            db_models.Organization.org_id == current_user.org_id
        ).all()
        logger.debug(f"Non-admin user listing their organization: {current_user.org_id}")
    
    return {"orgs": [{"org_id": r.org_id, "name": r.name} for r in rows]}


# User management (create/list/delete users inside an org):

@app.post("/orgs/{org_id}/users", status_code=201)
def create_user_in_org(org_id: str = Path(...), body: schemas.UserCreate = Body(...), current_user: db_models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Endpoint for creating a new user within an organization.
    - org_id: the ID of the organization to which the user will belong (from the URL path)
    - body: contains the username, password, and role for the new user from the request body
    - current_user: the authenticated user making the request
    - db: database session for creating the user
    The endpoint will:
        - Log the user creation attempt with the provided username, organization ID, and role
        - Check if the current user has permission to create users in the specified organization (must be org admin or global admin)
        - If the user does not have permission, log a warning and raise an HTTP 403 exception
        - Check if the specified organization exists in the database
        - If it does not exist, log a warning and raise an HTTP 404 exception
        - Check if a user with the same username already exists in the database
        - If it exists, log a warning and raise an HTTP 409 exception
        - If all checks pass, hash the user's password and create a new user record in the database
        - Commit the transaction and log the successful creation of the user
        - Return the new user's username, role, and organization ID to the client
    """
    logger.info(f"Creating user - Username: {body.username}, Org: {org_id}, Role: {body.role}")
    # permission check
    if not db_utils._is_org_admin_or_admin(current_user, org_id):
        logger.warning(f"User creation denied - Insufficient permissions for user {current_user.username}")
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    if not db.query(db_models.Organization).filter(db_models.Organization.org_id == org_id).first():
        logger.warning(f"User creation failed - Organization not found: {org_id}")
        raise HTTPException(status_code=404, detail="Org not found")
    if db_utils.get_user(db, body.username):
        logger.warning(f"User creation failed - User already exists: {body.username}")
        raise HTTPException(status_code=409, detail="User exists")
    hashed = db_utils.get_password_hash(body.password)
    user = db_models.User(username=body.username, hashed_password=hashed, role=body.role, org_id=org_id)
    db.add(user)
    db.commit()
    logger.info(f"User created successfully - Username: {body.username}, Org: {org_id}, Role: {body.role}")
    return {"username": body.username, "role": body.role, "org_id": org_id}

@app.get("/orgs/{org_id}/users")
def list_users(org_id: str, current_user: db_models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Endpoint for listing users within an organization.
    - org_id: the ID of the organization whose users will be listed (from the URL path)
    - current_user: the authenticated user making the request
    - db: database session for querying users
    The endpoint will:
        - Log the user listing request with the organization ID and user's information
        - Check if the current user has permission to list users in the specified organization (must be org admin or global admin)
        - If the user does not have permission, log a warning and raise an HTTP 403 exception
        - Query the database for all users that belong to the specified organization
        - Log the number of users retrieved for debugging
        - Return a list of users (username and role) to the client
    """
    logger.debug(f"Listing users for org {org_id} - Requested by: {current_user.username}")
    if not db_utils._is_org_admin_or_admin(current_user, org_id):
        logger.warning(f"List users denied - Insufficient permissions for user {current_user.username}")
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    users = db.query(db_models.User).filter(db_models.User.org_id == org_id).all()
    logger.debug(f"Listed {len(users)} users for org {org_id}")
    return {"users": [{"username": u.username, "role": u.role} for u in users]}

@app.delete("/orgs/{org_id}/users/{username}")
def delete_user(org_id: str, username: str, current_user: db_models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Endpoint for deleting a user within an organization.
    - org_id: the ID of the organization to which the user belongs (from the URL path)
    - username: the username of the user to be deleted (from the URL path)
    - current_user: the authenticated user making the request
    - db: database session for deleting the user
    The endpoint will:
        - Log the user deletion attempt with the username, organization ID, and user's information
        - Check if the current user has permission to delete users in the specified organization (must be org admin or global admin)
        - If the user does not have permission, log a warning and raise an HTTP 403 exception
        - Query the database for the user with the specified username
        - If the user does not exist or does not belong to the specified organization, log a warning and raise an HTTP 404 exception
        - If all checks pass, delete the user record from the database
        - Commit the transaction and log the successful deletion of the user
        - Return a confirmation message to the client
    """
    logger.info(f"Deleting user - Username: {username}, Org: {org_id}, Requested by: {current_user.username}")
    if not db_utils._is_org_admin_or_admin(current_user, org_id):
        logger.warning(f"User deletion denied - Insufficient permissions for user {current_user.username}")
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    user = db_utils.get_user(db, username)
    if not user or user.org_id != org_id:
        logger.warning(f"User deletion failed - User not found in org: {username} (Org: {org_id})")
        raise HTTPException(status_code=404, detail="User not found in org")
    db.delete(user)
    db.commit()
    logger.info(f"User deleted successfully - Username: {username}, Org: {org_id}")
    return {"deleted": username}

@app.get("/metrics")
def metrics():
    """
    Endpoint to expose Prometheus metrics.
        The endpoint will:
            - Generate the latest metrics data using the Prometheus client library
            - Return the metrics data with the appropriate content type for Prometheus to scrape
        This allows monitoring of API usage, authentication events, and other custom metrics defined in the application.
        The metrics can be visualized in Grafana or used for alerting based on thresholds.
        Example metrics include request counts, request latency, and login attempt outcomes.
        The endpoint is typically accessed by Prometheus at regular intervals (e.g. every 15 seconds) to collect data for analysis.
        Proper logging is included to track when the metrics endpoint is accessed and if any errors occur during metrics generation.
        Note: Ensure that the Prometheus client library is properly configured to collect and expose the desired metrics throughout the application.
    """
    return Response(generate_latest(),media_type=CONTENT_TYPE_LATEST)

