-- Create the Books table
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY,  -- SQLite obsługuje AUTO_INCREMENT automatycznie przy PRIMARY KEY
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    isbn TEXT UNIQUE NOT NULL,
    available BOOLEAN DEFAULT 1
);

-- Create the Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL
);

-- Create the Loans table
CREATE TABLE IF NOT EXISTS loans (
    id INTEGER PRIMARY KEY,
    book_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    loan_date DATE NOT NULL DEFAULT (DATE('now')),
    return_date DATE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Index to speed up lookups on available books
CREATE INDEX IF NOT EXISTS idx_books_available ON books (available);
