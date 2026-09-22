from fastapi import APIRouter, Request, Query # Works with the requests made to the API
from fastapi.responses import FileResponse # Send files as a response
from data.auth import get_userid # Works with the auth.py file to get the user_id
from openpyxl import Workbook # import the Workbook class from openpyxl
from pathlib import Path # Work with file paths easily
import sqlite3 # DB
import zipfile # Work with zip files
import tempfile # Create temporary files and directories
import shutil # High-level file operations like copying and removing files and directories

router = APIRouter()
dbconn = sqlite3.connect('/app/data/database.db', check_same_thread=False)

# Endpoint for exporting receipts as an Excel file and a ZIP file
@router.get("/export/")
def export_receipts(
    request: Request,
    payment_method: str | None = Query(default=None),
    category: str | None = Query(default=None),
    merchant: str | None = Query(default=None),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None)
    ):

    # gets the session_id with auth.py
    user_id = get_userid(request)

    # Build the SQL query based on the provided filters
    query = "SELECT id, amount, date, merchant, payment_method, category, image_path FROM receipts WHERE user_id = ?"

    params = [user_id]
    
    # Check if the filters are provided and add them to the query and params list
    if payment_method:
        query += " AND payment_method = ?"
        params.append(payment_method)

    if category:
        query += " AND category = ?"
        params.append(category)
    
    if merchant:
        query += " AND merchant = ?"
        params.append(merchant)
    
    if date_from:
        query += " AND date >= ?"
        params.append(date_from)

    if date_to:
        query += " AND date <= ?"
        params.append(date_to)

    # Execute the query and fetch the receipts
    receipts = dbconn.execute(query, params).fetchall()

    # Create a temporary directory to store the Excel file and photos
    temp_dir = Path(tempfile.mkdtemp())
    photos_dir = temp_dir / "photos"
    photos_dir.mkdir(parents=True, exist_ok=True)

    # Create paths for the Excel file and ZIP file
    excel_file_path = temp_dir / "receipts.xlsx"
    zip_file_path = temp_dir / "receipts.zip"

    try:
        # Create an Excel workbook and add a worksheet
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Receipts"
        
        # Add headers to the Excel sheet
        sheet.append(["ID", "Amount", "Date", "Merchant", "Payment Method", "Category", "Image Path"])
        # In a future update, the excel will be traduced to the language of the user, but for now it will be in english only


        # Repeat for each receipt, add a row to the Excel sheet and copy the image to the photos directory
        for receipt in receipts:

            # Unpack the receipt data for each receipt
            receipt_id = receipt[0]
            amount = receipt[1]
            date = receipt[2]
            merchant = receipt[3]
            payment_method = receipt[4]
            Category = receipt[5]
            image_url = Path(receipt[6])  # Get the image path from the database

            image_name = Path(image_url).name

            # The image_path on the server is the image_url, but we need to get the actual path on the server
            image_path = Path("/app/receipts/uploads") / image_name

            # Add a row to the Excel sheet with the receipt data
            sheet.append([receipt_id, amount, date, merchant, payment_method, Category, image_name])

            # Copy the receipt image to the photos directory
            if image_path.exists():
                shutil.copy(image_path, photos_dir / image_name)
            
        # Save the Excel workbook to the temporary directory
        workbook.save(excel_file_path)

        # Create a ZIP file containing the Excel file and photos
        with zipfile.ZipFile(zip_file_path, 'w') as zipf:
            # Add the Excel file to the ZIP file
            zipf.write(excel_file_path, arcname="receipts.xlsx")
            for photo in photos_dir.iterdir():
                # Add each photo to the ZIP file under the "photos" directory
                zipf.write(photo, arcname=f"photos/{photo.name}")

        # Return the ZIP file as a response
        return FileResponse(path=str(zip_file_path), media_type="application/zip", filename="receipts.zip")
    except Exception as e:
        # Handle any exceptions that occur during the process
        return {"error": str(e)}