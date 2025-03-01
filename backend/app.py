from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import os
from database import connect, add_user, add_book, get_books, get_users, borrow_book, return_book, export_loans

app = Flask(__name__)
app.secret_key = "your_secret_key"

@app.route('/')
def index():
    """Render homepage."""
    return render_template('index.html')

@app.route('/manage', methods=['GET', 'POST'])
def manage():
    """Manage users and books."""
    if request.method == 'POST':
        if 'add_user' in request.form:
            user_name = request.form.get('user_name')
            user_email = request.form.get('user_email')

            if user_name and user_email:
                try:
                    add_user(user_name, user_email)
                    flash("User added successfully!", "success")
                except Exception as e:
                    flash(f"Error adding user: {e}", "error")
            else:
                flash("Please fill in all fields.", "error")

        elif 'add_book' in request.form:
            book_title = request.form.get('book_title')
            book_author = request.form.get('book_author')
            book_isbn = request.form.get('book_isbn')

            if book_title and book_author and book_isbn:
                try:
                    add_book(book_title, book_author, book_isbn)
                    flash("Book added successfully!", "success")
                except Exception as e:
                    flash(f"Error adding book: {e}", "error")
            else:
                flash("Please fill in all fields.", "error")

        return redirect(url_for('manage'))

    users = get_users()
    books = get_books()

    return render_template('manage.html', users=users, books=books)

@app.route('/borrow', methods=['GET', 'POST'])
def borrow():
    """Handle book borrowing and returning."""
    if request.method == 'POST':
        action = request.form.get('action')
        user_id = request.form.get('user_id')
        book_id = request.form.get('book_id')
        loan_id = request.form.get('loan_id')

        if action == "borrow" and user_id and book_id:
            try:
                borrow_book(user_id, book_id)
                flash("Book borrowed successfully!", "success")
            except Exception as e:
                flash(f"Error borrowing book: {e}", "error")

        elif action == "return" and loan_id:
            try:
                # Fetch book_id from loan_id
                conn = connect()
                cursor = conn.cursor()
                cursor.execute("SELECT book_id FROM loans WHERE id = %s", (loan_id,))
                loan = cursor.fetchone()
                conn.close()

                if loan:
                    book_id = loan[0]
                    return_book(book_id)
                    flash("Book returned successfully!", "success")
                else:
                    flash("Invalid loan selected.", "error")
            except Exception as e:
                flash(f"Error returning book: {e}", "error")

        return redirect(url_for('borrow'))

    users = get_users()
    books = get_books()

    # Fetch active loans for return dropdown
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT loans.id, books.title, users.name, books.id as book_id
        FROM loans
        JOIN books ON loans.book_id = books.id
        JOIN users ON loans.user_id = users.id
        WHERE loans.return_date IS NULL
    """)
    loans = cursor.fetchall()
    conn.close()

    return render_template('borrow.html', users=users, books=books, loans=loans)


@app.route('/export', methods=['GET', 'POST'])
def export():
    """Export loans data."""
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        file_path = export_loans(start_date, end_date)
        return send_file(file_path, as_attachment=True)

    return render_template('export.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
