# Dependencies
import os # Add os for environment variables
from zoneinfo import ZoneInfo # Add ZoneInfo for timezone handling
from datetime import datetime, timedelta # Add timedelta import
from fastapi import APIRouter, HTTPException, Response, Request ,Cookie # Add fastapi dependencies
from fastapi.responses import RedirectResponse # Add fastapi redirection response
from pydantic import BaseModel # Add pydantic for data validation ( create models for request and response data)
from data.auth import get_userid # Add get_userid function from auth.py
from .email import send_invitation_email # Add send_invitation_email function from email.py
import sqlite3 # Add sqlite3 for database operations
import bcrypt # Add bcrypt for password hashing
import secrets # Add secrets for generating secure tokens

router = APIRouter()
dbconn = sqlite3.connect('/app/data/database.db', check_same_thread=False)
TIMEZONE = os.getenv("TZ", "UTC")  # Default to UTC if TZ is not set


# Create the users table if it doesn't exist
dbconn.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    language TEXT NOT NULL DEFAULT 'en',
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)''')

# Create the sessions table if it doesn't exist
dbconn.execute('''CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    expires_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
)''')

# Create the register invitaion table if it doesn't exist
dbconn.execute('''CREATE TABLE IF NOT EXISTS invitations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    language TEXT NOT NULL DEFAULT 'en',
    code TEXT NOT NULL UNIQUE,
    created_by INTEGER NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL DEFAULT (DATETIME('now', '+7 days')),
    FOREIGN KEY (created_by) REFERENCES users (id)
)''')

dbconn.commit()

# Pydantic models
class UserRegister(BaseModel):
    token: str
    username: str
    email: str
    password: str
    language: str | None = 'en'  # Optional language field with default value 'en'

class UserLogin(BaseModel):
    username: str
    password: str

class UserInvitation(BaseModel):
    email: str
    language: str | None = 'en'  # Optional language field with default value 'en'

# Convert utc time to local time based on the timezone set in the environment variable
def utc_to_local(date_string):
    utc_date = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
    utc_date = utc_date.replace(tzinfo=ZoneInfo("UTC"))
    local_date = utc_date.astimezone(ZoneInfo(TIMEZONE))
    return local_date.strftime("%Y-%m-%d %H:%M:%S")

# Register user endpoint
@router.post("/register")
def register_user(user: UserRegister):

    # Check if the invitation token is valid
    invitation = dbconn.execute(
        "SELECT * FROM invitations WHERE code = ?",
        (user.token,)
    ).fetchone()

    if not invitation:
        raise HTTPException(status_code=400, detail="INVITATION_NOT_FOUND")

    # Check if the username or email already exists
    existing_user = dbconn.execute(
        "SELECT * FROM users WHERE username = ? OR email = ?",
        (user.username, user.email)
    ).fetchone()

    # Error handling for existing user
    if existing_user:
        raise HTTPException(status_code=400, detail="USERNAME_TAKEN")

    # Hash the password before storing it in the database 
    hashed_password = bcrypt.hashpw(
        user.password.encode('utf-8'), bcrypt.gensalt()
    ) .decode('utf-8')
    
    # Insert the new user into the database
    dbconn.execute(
        "INSERT INTO users (username, email, password, language) VALUES (?, ?, ?, ?)",
        (user.username, user.email, hashed_password, user.language)
    )

    # Delete the invitation after successful registration
    dbconn.execute(
        "DELETE FROM invitations WHERE code = ?",
        (user.token,)
    )

    dbconn.commit()

    # Return a success message
    return RedirectResponse(
        url="/credentials/login.html?code=201",
        status_code=303
    )

# Login user endpoint
@router.post("/login")
def login_user(response: Response, user: UserLogin):

    # Function to handle invalid username or password
    def invalid_username():
        raise HTTPException(
        status_code=401,
        detail="254"
        )

    # Query the database for the user by username
    database_user = dbconn.execute(
        "SELECT * FROM users WHERE username = ?",
        (user.username,)
    ).fetchone()

    # Check if the user exists
    if not database_user:
        invalid_username()

    # Unpack the user data from the database  
    user_id, language, username, email, hashed_password = database_user

    # Verify the provided password against the hashed password in the database
    if not bcrypt.checkpw(user.password.encode('utf-8'), hashed_password.encode('utf-8')):
        invalid_username()
    
    # Create a session ID for the user
    session_id = secrets.token_urlsafe(32) 

    # Set the session expiration time (e.g., 7 days from now)
    expires_at = datetime.utcnow() + timedelta(days=7)

    # Insert the session into the database
    dbconn.execute(
        "INSERT INTO sessions (id, user_id, expires_at) VALUES (?, ?, ?)",
        (session_id, user_id, expires_at)
    )
    dbconn.commit()

    # Add a redirection to the response
    response = RedirectResponse(
        url="/index.html",
        status_code=303
    )

    # Add the session ID on the cookie on the response
    response.set_cookie(
        key="session_id", 
        value=session_id,
        httponly=True,
        samesite="lax",
        max_age=7 * 24 * 60 * 60  # 7 days in seconds
    )

    # Add the language on the cookie on the response
    response.set_cookie(
        key="language", 
        value=language,
        httponly=False,
        samesite="lax",
        max_age=7 * 24 * 60 * 60  # 7 days in seconds
    )

    # Return the response with the session cookie and redirection to the index page all together
    return response

# Invitaition endpoint
@router.post("/invitations")
async def create_invitation(request: Request, invitation: UserInvitation):
    
    # Gets the user_id from the session cookie
    user_id = get_userid(request)

    # Get the email and language from the invitation object
    email = invitation.email
    language = invitation.language

    # Check if the email is provided
    if not email:
        raise HTTPException(status_code=400, detail="EMAIL_REQUIRED")

    # Check if the language is provided
    if not language:
        raise HTTPException(status_code=400, detail="LANGUAGE_REQUIRED")

    # Check if the email already exists in the users table
    existing_user = dbconn.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,)
    ).fetchone()

    # Error handling for existing email
    if existing_user:
        raise HTTPException(status_code=400, detail="EMAIL_IN_USE")

    # Check if the email already exists in the invitations table
    existing_invitation = dbconn.execute(
        "SELECT * FROM invitations WHERE email = ?",
        (email,)
    ).fetchone()

    # Error handling for existing invitation
    if existing_invitation:
        raise HTTPException(status_code=400, detail="INVITATION_ALREADY_SENT")


    # Generate a unique invitation code
    token = secrets.token_urlsafe(32)

    # Insert the invitation into the database
    dbconn.execute(
        "INSERT INTO invitations (email, language, code, created_by) VALUES (?, ?, ?, ?)",
        (email, language, token, user_id)
    )
    dbconn.commit()

    # Send the invitation email
    send_invitation_email(token)

    return {"message": "INVITATION_SENT_SUCCESS"}

# Delete invitation endpoint
@router.post("/invitations/delete")
async def delete_invitation(request: Request):

    # Gets the user_id from the session cookie
    user_id = get_userid(request)

    try:
        data = await request.json()
        invitation_id = int(data["id"])
    except (KeyError, ValueError):
        raise HTTPException(status_code=400, detail="INVALID_INVITATION_ID")

    # Check if the invitation exists and belongs to the user
    existing_invitation = dbconn.execute(
        "SELECT * FROM invitations WHERE id = ? AND created_by = ?",
        (invitation_id, user_id)
    ).fetchone()

    if not existing_invitation:
        raise HTTPException(status_code=404, detail="INVITATION_NOT_FOUND")

    # Delete the invitation from the database
    dbconn.execute(
        "DELETE FROM invitations WHERE id = ? AND created_by = ?",
        (invitation_id, user_id)
    )
    dbconn.commit()

    return {"message": "INVITATION_DELETED_SUCCESS"}

# Consult invitations endpoint
@router.get("/invitations_list")
def list_invitations(request: Request):
    # Gets the user_id from the session cookie
    user_id = get_userid(request)

    # Query the database for invitations created by the user
    invitations = dbconn.execute(
        "SELECT id, email, language, created_at, expires_at FROM invitations WHERE created_by = ?",
        (user_id,)
    ).fetchall()

    # Convert the invitations to a list of dictionaries
    invitation_list = [
        {
            
            "id": invitation[0],
            "email": invitation[1],
            "language": invitation[2],
            "created_at": invitation[3],
            "expires_at": invitation[4]
        }
        for invitation in invitations
    ]

    return {"invitations": [
        {
            "id": invitation["id"],
            "email": invitation["email"],
            "language": invitation["language"],
            "created_at": utc_to_local(invitation["created_at"]),
            "expires_at": utc_to_local(invitation["expires_at"])
        }
        for invitation in invitation_list
    ]}

# Validate invitation endpoint
@router.post("/invitations/validate")
async def validate_invitation(request: Request):

    # Get the token from the request
    data = await request.json()
    token = data.get("token")

    # Query the database for the invitation by token
    invitation = dbconn.execute(
        "SELECT email, language, expires_at FROM invitations WHERE code = ?",
        (token,)
    ).fetchone()

    # Check if the invitation exists
    if not invitation:
        raise HTTPException(status_code=404, detail="INVITATION_NOT_FOUND")

    email, language, expires_at = invitation

    # Check if the invitation has expired
    if datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S") < datetime.utcnow():
        raise HTTPException(status_code=400, detail="INVITATION_EXPIRED")

    return {
        "email": email,
        "language": language,
    }

# Logout user endpoint
@router.post("/logout")
def logout(request: Request,response: Response):
    # Get the session ID from the cookie
    session_id = request.cookies.get("session_id")

    if not session_id:
        # If the session ID is not found, redirect to the login page
        return RedirectResponse(url="/credentials/login.html?code=251",
        status_code=303
        )
    
    # Delete the session from the database
    dbconn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    dbconn.commit()

    # The redirect added to the main response
    response = RedirectResponse(
        url="/credentials/login.html?code=250",
        status_code=303
    )

    # Delete the session ID from the cookie
    response.delete_cookie(key="session_id")

    return response