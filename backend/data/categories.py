from fastapi import APIRouter, Request, File, Form, HTTPException # Import FastAPI modules
from fastapi.responses import FileResponse # Import FastAPI redirect response
from data.auth import get_userid # Import the get_userid function from the auth module
import sqlite3


# Create a receipt category table if it doesn't exist
dbconn.execute('''CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id),
    UNIQUE(user_id, name)
)''')

dbconn.execute('''CREATE TABLE IF NOT EXISTS payment_methods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    last_digits TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id),
    UNIQUE(user_id, name, last_digits)
)''')


dbconn.commit()


# CATEGORIES

# The endpoint for listing all categories for the user
@router.get("/categories/")
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

# PAYMENT METHODS

# The endpoint for listing all payment methods for the user
@router.get("/payment-methods/")
def list_payment_methods(request: Request):

    user_id = get_userid(request)

    payment_methods = dbconn.execute("SELECT name, last_digits FROM payment_methods WHERE user_id = ?",(user_id,)).fetchall()

    return[{"name": method[0], "last_digits": method[1]} for method in payment_methods]

# The endpoint for adding a new payment method for the user
@router.post("/payment-methods/add")
def add_payment_method(
    request: Request,
     name: str = Form(...),
     last_digits: str = Form(...)
     ):

    user_id = get_userid(request)

    # Check if the payment method already exists for the user
    existing_method = dbconn.execute("SELECT id FROM payment_methods WHERE user_id = ? AND name = ? AND last_digits = ?", (user_id, name, last_digits)).fetchone()
    if existing_method:
        raise HTTPException(status_code=400, detail="PAYMENT_METHOD_EXISTS")

    # Insert the new payment method into the database
    dbconn.execute("INSERT INTO payment_methods (name, last_digits, user_id) VALUES (?, ?, ?)", (name, last_digits, user_id))
    dbconn.commit()

    return {"message": "PAYMENT_METHOD_ADDED"}

# The endpoint for deleting a payment method for the user
@router.post("/payment-methods/delete")
def delete_payment_method(request: Request, name: str = Form(...), last_digits: str = Form(...)):

    user_id = get_userid(request)

    # Check if the payment method exists for the user
    existing_method = dbconn.execute("SELECT id FROM payment_methods WHERE user_id = ? AND name = ? AND last_digits = ?", (user_id, name, last_digits)).fetchone()
    if not existing_method:
        raise HTTPException(status_code=404, detail="PAYMENT_METHOD_NOT_FOUND")

    # Delete the payment method from the database
    dbconn.execute("DELETE FROM payment_methods WHERE user_id = ? AND name = ? AND last_digits = ?", (user_id, name, last_digits))
    dbconn.commit()

    return {"message": "PAYMENT_METHOD_DELETED"}

