from fastapi import APIRouter, Request, Response # FastAPI imports
from fastapi.responses import RedirectResponse # FastAPI for redirecting to another page
from datetime import datetime # For checking if the session is expired
import sqlite3 # For connecting to the database

dbconn = sqlite3.connect('/app/data/database.db', check_same_thread=False)
router = APIRouter()

# Endpoint for verifing the cookies/session_id
@router.get("/")
def check_session(request: Request, response: Response):

    session_id = request.cookies.get("session_id")
    
    # Check if the cookie is there
    if session_id:

        # Check if the session_id exists in the DB. If not, erase the cookies
        session = dbconn.execute("SELECT * FROM sessions WHERE id = ?",(session_id,)).fetchone()
        if not session:   
            response = RedirectResponse(url="/credentials/login.html?code=252", status_code=303)
            response.delete_cookie("session_id")
            return response
        
        # Check if it is expired, if it is, deletes session_id on the DB/Cookie
        expires_at = session[2]

        if datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S.%f") < datetime.now():
            dbconn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            dbconn.commit()
            response = RedirectResponse(url="/credentials/login.html?code=253", status_code=303)
            response.delete_cookie("session_id")
            return response

        return {"message": "200"}
    else:
        return RedirectResponse(url="/credentials/login.html?code=251", status_code=303)


# Verifies the cookies/session_id. Keeps them up to date and dont do redirects. It is used in register and login
@router.get("/cookies_state")
def check_only_cookies(request: Request, response: Response):

    session_id = request.cookies.get("session_id")

    # Verifies if there is a cookie. If not, continues
    if (session_id):

        # Check if the session_id exists in the DB. If not, delete actual cookie and continues.
        session = dbconn.execute("SELECT * FROM sessions WHERE id = ?",(session_id,)).fetchone()
        if not session:
            response.delete_cookie("session_id")
            return {"message": "200"}

        # Check if it is expired. If it is, deletes actual cookie and session_id on DB
        expires_at = session[2]

        if datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S.%f") < datetime.now():
            dbconn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            dbconn.commit()
            response.delete_cookie("session_id")
            return {"message": "200"}
    
        return RedirectResponse(url="/index.html", status_code=303)
    else:
        return {"message": "200"}
    
# This cannot work if / isn't called before, This function will get quickly the user_id from the session_id cookie
def get_userid(request: Request):

    # Goes directly looking for session_id and then user_id. Send it directly back
    session_id = request.cookies.get("session_id")
    session = dbconn.execute("SELECT user_id FROM sessions WHERE id = ?",(session_id,)).fetchone()
    user_id = session[0]
    return user_id