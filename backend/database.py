import sqlite3
import pandas as pd

DB_FILE = 'library.db'

def connect():
    return sqlite3.connect(DB_FILE)

def add_book(title, author, isbn):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO books (title, author, isbn, available) VALUES (?, ?, ?, 1)", (title, author, isbn))
    conn.commit()
    conn.close()

def add_user(name, email):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
    conn.commit()
    conn.close()

def get_books():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    conn.close()
    return books

def get_users():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

def borrow_book(user_id, book_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE books SET available = 0 WHERE id = ?", (book_id,))
    cursor.execute("INSERT INTO loans (book_id, user_id, loan_date) VALUES (?, ?, DATE('now'))", (book_id, user_id))
    conn.commit()
    conn.close()

def return_book(book_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE books SET available = 1 WHERE id = ?", (book_id,))
    cursor.execute("UPDATE loans SET return_date = DATE('now') WHERE book_id = ? AND return_date IS NULL", (book_id,))
    conn.commit()
    conn.close()

def export_loans(start_date, end_date):
    conn = connect()
    query = "SELECT * FROM loans WHERE loan_date BETWEEN ? AND ?"
    df = pd.read_sql_query(query, conn, params=(start_date, end_date))
    file_path = "loans_export.xlsx"
    df.to_excel(file_path, index=False)
    conn.close()
    return file_path
