from fastapi import APIRouter, Request, UploadFile, File, Form, HTTPException # Import FastAPI modules
from fastapi.responses import FileResponse # Import FastAPI redirect response
from pydantic import BaseModel  # Import Pydantic BaseModel for data validation
from PIL import Image  # Import Pillow for image processing
from pathlib import Path # Import Path for file path handling
from data.auth import get_userid # Import the get_userid function from the auth module
import uuid
import sqlite3

# Upload directory for the receipt image
UPLOAD_DIR = Path("/app/receipts/uploads")
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
    category TEXT NOT NULL,
    description TEXT,
    image_path TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
)''')

# Create a receipt category table if it doesn't exist
dbconn.execute('''CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id),
    UNIQUE(user_id, name)
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
    category: str = Form(...),
    description: str | None = Form(None),
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

    # Convert image to JPG
    if image.mode != "RGB":
        image = image.convert("RGB")
    
    image.save(file_path, format="JPEG", quality=85)

    # Insert the receipt into the database
    dbconn.execute(
        "INSERT INTO receipts (user_id, amount, date, merchant, payment_method, category, description, image_path) VALUES (?, ?, date('now', 'localtime'), ?, ?, ?, ?, ?)",
        (user_id, amount, merchant, payment_method, category, description, str(file_url))
    )

    dbconn.commit()
    return {"message": "RECEIPT_ADDED"}

@router.post("/receipts/delete")
def delete_receipt(request: Request, receipt_id: int = Form(...)):

    user_id = get_userid(request)

    # Check if the receipt exists and belongs to the user
    existing_receipt = dbconn.execute("SELECT image_path FROM receipts WHERE id = ? AND user_id = ?", (receipt_id, user_id)).fetchone()

    if not existing_receipt:
        raise HTTPException(status_code=404, detail="RECEIPT_NOT_FOUND.")

    # Delete the image file associated with the receipt
    image_path = existing_receipt[0]
    file_path = UPLOAD_DIR / Path(image_path).name
    if file_path.exists():
        file_path.unlink()  # Delete the file
    
    # Delete the receipt from the database
    dbconn.execute("DELETE FROM receipts WHERE id = ? AND user_id = ?", (receipt_id, user_id))
    dbconn.commit()

    return {"message": "RECEIPT_DELETED"}

# The endpoint so if someone goes to /receipts/file.jpg/ it takes him to the photo.
@router.get("/receipts/{filename}")
async def get_image(filename: str):
    file_path = UPLOAD_DIR / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="IMAGE_NOT_FOUND")

    return FileResponse(file_path)

# The endpoint for listing all receipts for the user
@router.get("/receipts")
def list_receipt(request: Request):

    user_id = get_userid(request)

    # Get all receipts for the user from the database and return them as a list of dictionaries
    receipts = dbconn.execute("SELECT amount, date, merchant, payment_method, category, description, image_path FROM receipts WHERE user_id = ?",(user_id,)).fetchall()

    return[{"amount": receipt[0], "date": receipt[1], "merchant": receipt[2], "payment_method": receipt[3], "category": receipt[4], "description": receipt[5], "image_path": receipt[6]} for receipt in receipts]

# The endpoint for listing all categories for the user
@router.get("/categories")
def list_categories(request: Request):

    user_id = get_userid(request)

    categories = dbconn.execute("SELECT name, type FROM categories WHERE user_id = ?",(user_id,)).fetchall()

    return[{"name": category[0], "type": category[1]} for category in categories]

# The endpoint for adding a new category for the user
@router.post("/categories/add")
def add_category(
    request: Request,
     name: str = Form(...),
     type: str = Form(...)
     ):

    user_id = get_userid(request)

    # Check if the category already exists for the user
    existing_category = dbconn.execute("SELECT id FROM categories WHERE user_id = ? AND name = ?", (user_id, name)).fetchone()
    if existing_category:
        raise HTTPException(status_code=400, detail="CATEGORY_EXISTS")

    # Insert the new category into the database
    dbconn.execute("INSERT INTO categories (name, type, user_id) VALUES (?, ?, ?)", (name, type, user_id))
    dbconn.commit()

    return {"message": "CATEGORY_ADDED"}
# The endpoint for deleting a category for the user
@router.post("/categories/delete")
def delete_category(request: Request, name: str = Form(...)):

    user_id = get_userid(request)

    # Check if the category exists for the user
    existing_category = dbconn.execute("SELECT id FROM categories WHERE user_id = ? AND name = ?", (user_id, name)).fetchone()
    if not existing_category:
        raise HTTPException(status_code=404, detail="CATEGORY_NOT_FOUND")

    # Delete the category from the database
    dbconn.execute("DELETE FROM categories WHERE user_id = ? AND name = ?", (user_id, name))
    dbconn.commit()

    return {"message": "CATEGORY_DELETED"}



