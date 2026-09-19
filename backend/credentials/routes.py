# Dependencies
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Response, Request ,Cookie
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import sqlite3
import bcrypt
import secrets

router = APIRouter()
dbconn = sqlite3.connect('/app/data/database.db', check_same_thread=False)

# Create the users table if it doesn't exist
dbconn.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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


dbconn.commit()

# Pydantic models
class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str


# Register user endpoint
@router.post("/register")
def register_user(user: UserRegister):

    # Check if the username or email already exists
    existing_user = dbconn.execute(
        "SELECT * FROM users WHERE username = ? OR email = ?",
        (user.username, user.email)
    ).fetchone()

    # Error handling for existing user
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="The username or email is already registered"
        )

    # Hash the password before storing it in the database 
    hashed_password = bcrypt.hashpw(
        user.password.encode('utf-8'), bcrypt.gensalt()
    ) .decode('utf-8')
    
    # Insert the new user into the database
    dbconn.execute(
        "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
        (user.username, user.email, hashed_password)
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
        detail="Invalid username or password"
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
    user_id, username, email, hashed_password = database_user

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
    # Return the response with the session cookie and redirection to the index page all together
    return response

# Logout user endpoint
@router.post("/logout")
def logout(request: Request,response: Response ):
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

    # Delete the session ID from the cookie
    response.delete_cookie(key="session_id")

    # Redirect to the login page
    return RedirectResponse(url="/credentials/login.html?code=250",
    status_code=303
    )

# DONT FORGOT TO REMOVE THIS ON THE ULTIMATE VERSION
# Debugging endpoint to get all users (for testing purposes)
@router.get("/users")
def get_users():
    users = dbconn.execute("SELECT id, username, email, password FROM users").fetchall()
    return [{"id": user[0], "username": user[1], "email": user[2], "password": user[3]} for user in users]

@router.get("/sessions")
def get_sessions():
    sessions = dbconn.execute("SELECT id, user_id, expires_at FROM sessions").fetchall()
    return [{"id": session[0], "user_id": session[1], "expires_at": session[2]} for session in sessions]
