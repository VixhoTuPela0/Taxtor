from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
from datetime import datetime
from data.auth import router as auth_router
from data.auth import get_userid
from credentials.routes import router as credentials_router
from receipts.routes import router as receipts_router
from backup.routes import router as backup_router

import sqlite3


dbconn = sqlite3.connect('/app/data/database.db', check_same_thread=False)
app = FastAPI()
app.include_router(receipts_router)
app.include_router(credentials_router)
app.include_router(auth_router)
app.include_router(backup_router)

@app.post("/languages") # Endpoint for changing the language of the user in the DB
async def change_language(request: Request):
    # Get the user ID from the request
    user_id = get_userid(request)

    # Get the language from the request body and update the user's language in the database
    data = await request.json()
    language = data.get("language")
    dbconn.execute("UPDATE users SET language = ? WHERE id = ?", (language, user_id))
    dbconn.commit()

    # Set the language cookie in the response
    response =  JSONResponse({"message": "LANGUAGE_UPDATED"})
    response.set_cookie(
       key="language",
       value=language,
       max_age=31536000,
       samesite="lax" 
    )
    return response

@app.get("/languages") # Endpoint for getting the language of the user in the DB
def get_language(request: Request):
    # Get the user ID from the request
    user_id = get_userid(request)
    # Get the language from the database for the user and return it in the response
    language = dbconn.execute("SELECT language FROM users WHERE id = ?", (user_id,)).fetchone()[0]
    return {"language": language}