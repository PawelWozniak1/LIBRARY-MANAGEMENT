import mysql.connector
import os
import pandas as pd  # Import pandas for exporting data
from urllib.parse import urlparse

# Parse DATABASE_URL from environment variable
db_url = urlparse(os.getenv("DATABASE_URL"))

# DB configuration using parsed values
DB_CONFIG = {
    "host": db_url.hostname,
    "user": db_url.username,
    "password": db_url.password,
    "database": db_url.path.lstrip("/"),
}

def connect():
    """Establish database connection."""
    return mysql.connector.connect(**DB_CONFIG)

def add_book(title, author, isbn):
    """Add a new book to the database."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO books (title, author, isbn, available) VALUES (%s, %s, %s, 1)", 
                   (title, author, isbn))
    conn.commit()
    conn.close()

def add_user(name, email):
    """Add a new user to the database."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s)", (name, email))
    conn.commit()
    conn.close()

def get_books():
    """Retrieve all books from the database."""
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    conn.close()
    return books

def get_users():
    """Retrieve all users from the database."""
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

def borrow_book(user_id, book_id):
    """Borrow a book if available."""
    conn = connect()
    cursor = conn.cursor()

    # Check if book is available
    cursor.execute("SELECT available FROM books WHERE id = %s", (book_id,))
    result = cursor.fetchone()

    if not result or result[0] == 0:
        conn.close()
        return False  # Book is not available

    # Borrow the book
    cursor.execute("UPDATE books SET available = 0 WHERE id = %s", (book_id,))
    cursor.execute("INSERT INTO loans (book_id, user_id, loan_date) VALUES (%s, %s, CURDATE())", 
                   (book_id, user_id))
    conn.commit()
    conn.close()
    return True

def return_book(book_id):
    """Return a borrowed book."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE books SET available = 1 WHERE id = %s", (book_id,))
    cursor.execute("UPDATE loans SET return_date = CURDATE() WHERE book_id = %s AND return_date IS NULL", 
                   (book_id,))
    conn.commit()
    conn.close()

def export_loans(start_date, end_date):
    """Export loan data to an Excel file."""
    conn = connect()
    query = "SELECT * FROM loans WHERE loan_date BETWEEN %s AND %s"
    df = pd.read_sql(query, conn, params=(start_date, end_date))
    file_path = "loans_export.xlsx"
    df.to_excel(file_path, index=False)
    conn.close()
    return file_path
