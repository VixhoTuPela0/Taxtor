from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sqlite3

router = APIRouter()
dbconn = sqlite3.connect('/app/data/database.db', check_same_thread=False)

dbconn.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)''')

dbconn.commit()

class UserRegister(BaseModel):
    username: str
    email: str
    password: str


@router.post("/register")
def register_user(user: UserRegister):

    existing_user = dbconn.execute(
        "SELECT * FROM users WHERE username = ? OR email = ?",
        (user.username, user.email)
    ).fetchone()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="The username or email is already registered"
        )
    
    dbconn.execute(
        "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
        (user.username, user.email, user.password)
    )
    dbconn.commit()

    return {
        "message": f"Usuario {user.username} registrado con éxito",
         "email": user.email
         }

@router.get("/users")
def get_users():
    users = dbconn.execute("SELECT id, username, email FROM users").fetchall()
    return [{"id": user[0], "username": user[1], "email": user[2]} for user in users]
