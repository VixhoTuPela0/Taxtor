from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from datetime import datetime
from credentials.routes import router as credentials_router
import sqlite3


dbconn = sqlite3.connect('/app/data/database.db', check_same_thread=False)
app = FastAPI()
app.include_router(credentials_router)

@app.get("/")
def home(request: Request):
    # Check if the user is logged in by checking the session cookie
    cookies = request.cookies
    session_id = cookies.get("session_id")

    if session_id:
        # Check if the session ID exists in the database
        session = dbconn.execute("SELECT * FROM sessions WHERE id = ?"
        , (session_id,)
        ).fetchone()
        
        # If the session is not found, return a message indicating that the user needs to log in
        if not session:
            return RedirectResponse(url="/credentials/login.html?code=252",
             status_code=303
             )
        
        # Retrieve the user ID and expiration time
        user_id = session[1]
        expires_at = session[2]

        # Check if the session has expired
        if datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S.%f") < datetime.now():
            dbconn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            dbconn.commit()
            return RedirectResponse(url="/credentials/login.html?code=253",
             status_code=303
             )
    
        # If the session is valid, retrieve the user information
        user = dbconn.execute("SELECT * FROM users WHERE id = ?",
        (user_id,)
        ).fetchone()

        return {"message": f"Welcome, {user[1]}!"} 

    else: 
        # If the session ID is not found, redirect to the login page
        return RedirectResponse(url="/credentials/login.html?code=251",
         status_code=303
         )
   