from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Configure the SQLite database
DATABASE = 'library.db'

# Create a table to store books
def create_books_table():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            author TEXT,
            publication_date DATE,
            isbn TEXT,
            copies_available INTEGER
        )
    ''')
    cursor.execute('''
    INSERT INTO books (title, author, publication_date, isbn, copies_available)
    VALUES
    ('Sample Book 1', 'Author A', '2022-01-15', 'ISBN123456', 5),
    ('Sample Book 2', 'Author B', '2021-05-20', 'ISBN789012', 3),
    ('Sample Book 3', 'Author C', '2023-03-10', 'ISBN345678', 2)
''')
    conn.commit()
    conn.close()

create_books_table()

# Home page to display the library catalog
@app.route('/')
def index():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM books')
    books = cursor.fetchall()
    conn.close()
    return render_template('index.html', books=books)

# Route to add a new book
@app.route('/add_book', methods=['POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        publication_date = request.form['publication_date']
        isbn = request.form['isbn']
        copies_available = request.form['copies_available']

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO books (title, author, publication_date, isbn, copies_available)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, author, publication_date, isbn, copies_available))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
