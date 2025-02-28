from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from database import add_book, add_user, get_books, get_users, borrow_book, return_book, export_loans
import sqlite3

app = Flask(__name__)
app.secret_key = "your_secret_key"

DATABASE = "library.db"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/manage', methods=['GET', 'POST'])
def manage():
    if request.method == 'POST':
        if 'add_user' in request.form:
            user_name = request.form.get('user_name')
            user_email = request.form.get('user_email')
            if user_name and user_email:
                with sqlite3.connect(DATABASE) as conn:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (user_name, user_email))
                    conn.commit()
                flash("User added successfully!", "success")
            else:
                flash("Please fill in all fields.", "error")

        elif 'add_book' in request.form:
            book_title = request.form.get('book_title')
            book_author = request.form.get('book_author')
            book_isbn = request.form.get('book_isbn')
            if book_title and book_author and book_isbn:
                with sqlite3.connect(DATABASE) as conn:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO books (title, author, isbn) VALUES (?, ?, ?)", (book_title, book_author, book_isbn))
                    conn.commit()
                flash("Book added successfully!", "success")
            else:
                flash("Please fill in all fields.", "error")

        return redirect(url_for('manage'))

    return render_template('manage.html')

@app.route('/borrow', methods=['GET', 'POST'])
def borrow():
    if request.method == 'POST':
        action = request.form.get('action')
        user_id = request.form.get('user_id')
        book_id = request.form.get('book_id')
        loan_id = request.form.get('loan_id')

        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()

            if action == "borrow":
                if user_id and book_id:
                    # Sprawdzamy, czy książka jest dostępna (available = 1)
                    cursor.execute("SELECT available FROM books WHERE id = ?", (book_id,))
                    is_available = cursor.fetchone()

                    if not is_available or is_available[0] == 0:
                        flash("This book is already borrowed!", "error")
                    else:
                        # Wypożyczamy książkę
                        cursor.execute("INSERT INTO loans (user_id, book_id, loan_date) VALUES (?, ?, DATE('now'))",
                                       (user_id, book_id))
                        # Ustawiamy `available = 0`
                        cursor.execute("UPDATE books SET available = 0 WHERE id = ?", (book_id,))
                        conn.commit()
                        flash("Book borrowed successfully!", "success")
                else:
                    flash("Please select both user and book.", "error")

            elif action == "return":
                if loan_id:
                    # Pobieramy book_id przed usunięciem rekordu z loans
                    cursor.execute("SELECT book_id FROM loans WHERE id = ?", (loan_id,))
                    book_id = cursor.fetchone()[0]

                    # Usuwamy wypożyczenie
                    cursor.execute("DELETE FROM loans WHERE id = ?", (loan_id,))
                    # Ustawiamy `available = 1`
                    cursor.execute("UPDATE books SET available = 1 WHERE id = ?", (book_id,))
                    conn.commit()
                    flash("Book returned successfully!", "success")
                else:
                    flash("Please select a loan to return.", "error")

        return redirect(url_for('borrow'))

    # Pobieramy użytkowników, dostępne książki oraz wypożyczone książki
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        users = cursor.execute("SELECT id, name FROM users").fetchall()
        books = cursor.execute("SELECT id, title FROM books WHERE available = 1").fetchall()
        loans = cursor.execute("""
            SELECT loans.id, books.title, users.name
            FROM loans
            JOIN books ON loans.book_id = books.id
            JOIN users ON loans.user_id = users.id
        """).fetchall()

    return render_template('borrow.html', users=users, books=books, loans=loans)

@app.route('/export', methods=['GET', 'POST'])
def export():
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        file_path = export_loans(start_date, end_date)
        return send_file(file_path, as_attachment=True)
    return render_template('export.html')

if __name__ == '__main__':
    app.run(debug=True)
