from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from datetime import datetime
from auth import router as auth_router
from credentials.routes import router as credentials_router
from receipts.routes import router as receipts_router
import sqlite3


dbconn = sqlite3.connect('/app/data/database.db', check_same_thread=False)
app = FastAPI()
app.include_router(receipts_router)
app.include_router(credentials_router)
app.include_router(auth_router)

