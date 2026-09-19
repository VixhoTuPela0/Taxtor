from fastapi import APIRouter, Request, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from PIL import Image
from pathlib import Path
from auth import get_userid
import uuid
import sqlite3

# Upload directory for the receipt image
UPLOAD_DIR = Path("/app/data/uploads/receipts")
UPLOAD_URL = "/api/receipts/"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter()
dbconn = sqlite3.connect('/app/data/database.db', check_same_thread=False)

# Create the receipts table if it doesn't exist
dbconn.execute('''CREATE TABLE IF NOT EXISTS receipts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    date DATETIME NOT NULL,
    merchant TEXT NOT NULL,
    payment_method TEXT NOT NULL,
    image_path TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
)''')

dbconn.commit()

# The endpoint for submitting the receipt
@router.post("/receipts")
def create_receipt(
    # Gets all the variables from the HTML
    request: Request,
    amount: float = Form(...),
    merchant: str = Form(...),
    payment_method: str = Form(...),
    invoice_image: UploadFile = File(...)
    ):
   
    # Verifies the session_id with auth.py
    user_id = get_userid(request)

    # Save the uploaded image
    filename = f"{uuid.uuid4()}.jpg"
    file_path = UPLOAD_DIR / filename
    file_url = f"{UPLOAD_URL}{filename}"

    # Open the uploaded image and convert it to JPEG format
    image = Image.open(invoice_image.file)

    if image.mode != "RGB":
        image = image.convert("RGB")
    
    image.save(file_path, format="JPEG", quality=85)

    # Insert the receipt into the database
    dbconn.execute(
        "INSERT INTO receipts (user_id, amount, date, merchant, payment_method, image_path) VALUES (?, ?, date('now', 'localtime'), ?, ?, ?)",
        (user_id, amount, merchant, payment_method, str(file_url))
    )

    dbconn.commit()
    return {"message": "Receipt created successfully."}

# The endpoint so if someone goes to /receipts/file.jpg/ it takes him to the photo.
@router.get("/receipts/{filename}")
async def get_image(filename: str):
    file_path = UPLOAD_DIR / filename

    if not file_path.exists():
        raise HTTPException(status_code=404)

    return FileResponse(file_path)

@router.get("/receipts")
def list_receipt(request: Request):

    user_id = get_userid(request)

    receipts = dbconn.execute("SELECT amount, date, merchant, payment_method, image_path FROM receipts WHERE user_id = ?",(user_id,)).fetchall()

    return[{"amount": receipt[0], "date": receipt[1], "merchant": receipt[2], "payment_method": receipt[3], "image_path": receipt[4]} for receipt in receipts]
    


