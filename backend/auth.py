from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from datetime import datetime
import sqlite3

dbconn = sqlite3.connect('/app/data/database.db', check_same_thread=False)
router = APIRouter()

# Endpoint for verifing the cookies/session_id
@router.get("/")
def check_session(request: Request):

    session_id = request.cookies.get("session_id")

    # Check if the cookie is there
    if not session_id:
        return RedirectResponse(url="/credentials/login.html?code=251", status_code=303)

    # Check if the session_id exists in the DB
    session = dbconn.execute("SELECT * FROM sessions WHERE id = ?",(session_id,)).fetchone()
    if not session:
        return RedirectResponse(url="/credentials/login.html?code=252", status_code=303)
    
    # Check if it is expired
    expires_at = session[2]

    if datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S.%f") < datetime.now():
        dbconn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        dbconn.commit()
        return RedirectResponse(url="/credentials/login.html?code=253", status_code=303)

    # If all is correct, return a success code
    return {"message": "200"}

# Only check if the cookies are present on the browser. It is used in register
@router.get("/only_cookies")
def check_only_cookies(request: Request):

    session_id = request.cookies.get("session_id")
    # Check if the cookie is there
    if session_id:
        return RedirectResponse(url="/index.html", status_code=303)

    return {"message": "200"}

# This cannot work if / isn't called before, /id wont check if cookie is alr
def get_userid(request: Request):

    # Goes directly looking for session_id and then user_id. Send it directly back
    session_id = request.cookies.get("session_id")
    session = dbconn.execute("SELECT user_id FROM sessions WHERE id = ?",(session_id,)).fetchone()
    user_id = session[0]
    return user_id