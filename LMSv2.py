from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
from datetime import datetime
from dotenv import load_dotenv
import os
import pymysql

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_CHARSET = os.getenv("DB_CHARSET")

def create_db_connection():
    connection = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset=DB_CHARSET
    )

    # Create tables if they don't exist
    with connection.cursor() as cursor:
        # Create books table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                book_id VARCHAR(50) UNIQUE NOT NULL,
                author VARCHAR(255),
                status VARCHAR(50) DEFAULT 'Available',
                issuer_id VARCHAR(50),
                course_code VARCHAR(50),
                issue_date DATETIME,
                return_date DATETIME
            )
        """)

        # Create users table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                
                is_admin BOOLEAN DEFAULT FALSE
            )
        """)

        # Insert admin user if it doesn't exist
        cursor.execute("""
            INSERT IGNORE INTO users (username, password, is_admin)
            VALUES ('admin', 'admin123', TRUE)
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS book_requests (
                id INT AUTO_INCREMENT PRIMARY KEY,
                book_id VARCHAR(50),
                user_id INT,
                status VARCHAR(20) DEFAULT 'Pending',
                request_date DATETIME,
                approval_date DATETIME,
                FOREIGN KEY (book_id) REFERENCES books(book_id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        cursor.execute("""
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'book_requests'
            AND COLUMN_NAME = 'notes'
        """)
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE book_requests ADD COLUMN notes TEXT")
        connection.commit()

    return connection

class BookListWidget(QWidget):
    def __init__(self, user_data=None):  # Add user_data parameter
        super().__init__()
        self.user_data = user_data  # Store user data
        self.setup_ui()
        self.load_books()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Search section
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search books by title, ID, author, or course code...")
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search_books)

        # Add filter dropdown
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Books", "Available Books", "My Requests"])
        self.filter_combo.currentTextChanged.connect(self.filter_books)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        search_layout.addWidget(self.filter_combo)

        # Book table
        self.book_table = QTableWidget()
        self.book_table.setColumnCount(8)  # Added one column for request button
        self.book_table.setHorizontalHeaderLabels([
            "Title", "Book ID", "Author", "Status",
            "Issuer", "Course Code", "Due Date", "Action"
        ])

        # Adjust column widths
        self.book_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        layout.addLayout(search_layout)
        layout.addWidget(self.book_table)

    def load_books(self):
        try:
            connection = create_db_connection()
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT b.*, r.status as request_status
                    FROM books b
                    LEFT JOIN book_requests r
                    ON b.book_id = r.book_id
                    AND r.user_id = %s
                """, (self.user_data.id if self.user_data else None,))
                books = cursor.fetchall()

                self.book_table.setRowCount(len(books))
                for i, book in enumerate(books):
                    for j, value in enumerate(book[1:8]):  # Skip ID, take next 7 fields
                        item = QTableWidgetItem(str(value) if value else "")
                        self.book_table.setItem(i, j, item)

                    # Add request button if user is not admin and book is available
                    if self.user_data and not self.user_data.is_admin:
                        request_button = QPushButton()
                        if book[4] == "Available":  # Status column
                            request_button.setText("Request")
                            request_button.clicked.connect(lambda checked, bid=book[2]: self.request_book(bid))
                        elif book[-1] == "Pending":  # Request status
                            request_button.setText("Pending")
                            request_button.setEnabled(False)
                        elif book[-1] == "Approved":
                            request_button.setText("Approved")
                            request_button.setEnabled(False)
                        else:
                            request_button.setText("Not Available")
                            request_button.setEnabled(False)

                        self.book_table.setCellWidget(i, 7, request_button)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load books: {str(e)}")
        finally:
            if 'connection' in locals():
                connection.close()

    def search_books(self):
        search_text = self.search_input.text()
        try:
            connection = create_db_connection()
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT b.*, r.status as request_status
                    FROM books b
                    LEFT JOIN book_requests r
                    ON b.book_id = r.book_id
                    AND r.user_id = %s
                    WHERE title LIKE %s
                    OR b.book_id LIKE %s
                    OR author LIKE %s
                    OR course_code LIKE %s
                """, (
                    self.user_data.id if self.user_data else None,
                    f"%{search_text}%",
                    f"%{search_text}%",
                    f"%{search_text}%",
                    f"%{search_text}%"
                ))
                books = cursor.fetchall()

                self.update_table(books)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Search failed: {str(e)}")
        finally:
            if 'connection' in locals():
                connection.close()

    def filter_books(self):
        filter_option = self.filter_combo.currentText()
        try:
            connection = create_db_connection()
            with connection.cursor() as cursor:
                if filter_option == "Available Books":
                    cursor.execute("""
                        SELECT b.*, r.status as request_status
                        FROM books b
                        LEFT JOIN book_requests r
                        ON b.book_id = r.book_id
                        AND r.user_id = %s
                        WHERE b.status = 'Available'
                    """, (self.user_data.id if self.user_data else None,))
                elif filter_option == "My Requests":
                    cursor.execute("""
                        SELECT b.*, r.status as request_status
                        FROM books b
                        INNER JOIN book_requests r
                        ON b.book_id = r.book_id
                        WHERE r.user_id = %s
                    """, (self.user_data.id,))
                else:  # All Books
                    cursor.execute("""
                        SELECT b.*, r.status as request_status
                        FROM books b
                        LEFT JOIN book_requests r
                        ON b.book_id = r.book_id
                        AND r.user_id = %s
                    """, (self.user_data.id if self.user_data else None,))

                books = cursor.fetchall()
                self.update_table(books)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Filter failed: {str(e)}")
        finally:
            if 'connection' in locals():
                connection.close()

    def request_book(self, book_id):
        try:
            connection = create_db_connection()
            with connection.cursor() as cursor:
                # Check user's current books and limits
                cursor.execute("""
                    SELECT book_limit, books_issued 
                    FROM users 
                    WHERE id = %s
                """, (self.user_data.id,))
                user_info = cursor.fetchone()
                book_limit = user_info[0]
                books_issued = user_info[1]

                if books_issued >= book_limit:
                    QMessageBox.warning(
                        self, 
                        "Limit Exceeded", 
                        f"You have reached your book limit ({book_limit} books)."
                    )
                    return

                # Check existing requests
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM book_requests 
                    WHERE user_id = %s AND status = 'Pending'
                """, (self.user_data.id,))
                pending_requests = cursor.fetchone()[0]

                if pending_requests + books_issued >= book_limit:
                    QMessageBox.warning(
                        self, 
                        "Limit Exceeded", 
                        f"You have too many pending requests. Please wait for approval."
                    )
                    return

                # Check if request already exists
                cursor.execute("""
                    SELECT * FROM book_requests 
                    WHERE book_id = %s AND user_id = %s AND status = 'Pending'
                """, (book_id, self.user_data.id))
                
                if cursor.fetchone():
                    QMessageBox.warning(self, "Warning", "You have already requested this book")
                    return

                # Create new request
                cursor.execute("""
                    INSERT INTO book_requests (book_id, user_id, status, request_date)
                    VALUES (%s, %s, 'Pending', NOW())
                """, (book_id, self.user_data.id))
                
                connection.commit()
                QMessageBox.information(self, "Success", "Book request submitted successfully!")
                self.load_books()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to request book: {str(e)}")
        finally:
            if 'connection' in locals():
                connection.close()

    def update_table(self, books):
        self.book_table.setRowCount(len(books))
        for i, book in enumerate(books):
            for j, value in enumerate(book[1:8]):
                item = QTableWidgetItem(str(value) if value else "")
                self.book_table.setItem(i, j, item)

            if self.user_data and not self.user_data.is_admin:
                request_button = QPushButton()
                if book[4] == "Available":
                    request_button.setText("Request")
                    request_button.clicked.connect(lambda checked, bid=book[2]: self.request_book(bid))
                elif book[-1] == "Pending":
                    request_button.setText("Pending")
                    request_button.setEnabled(False)
                elif book[-1] == "Approved":
                    request_button.setText("Approved")
                    request_button.setEnabled(False)
                else:
                    request_button.setText("Not Available")
                    request_button.setEnabled(False)

                self.book_table.setCellWidget(i, 7, request_button)
class ManageBooksWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.selected_book = None

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Book table for displaying and selecting books
        self.book_table = QTableWidget()
        self.book_table.setColumnCount(8)  # Added a column for return button
        self.book_table.setHorizontalHeaderLabels([
            "Title", "Book ID", "Author", "Status",
            "Issuer", "Course Code", "Due Date", "Actions"
        ])
        self.book_table.itemClicked.connect(self.book_selected)
        self.book_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        # Form for adding/editing books
        form_layout = QFormLayout()

        self.title_input = QLineEdit()
        self.book_id_input = QLineEdit()
        self.author_input = QLineEdit()
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Available", "Issued"])
        self.course_code_input = QLineEdit()

        form_layout.addRow("Title:", self.title_input)
        form_layout.addRow("Book ID:", self.book_id_input)
        form_layout.addRow("Author:", self.author_input)
        form_layout.addRow("Status:", self.status_combo)
        form_layout.addRow("Course Code:", self.course_code_input)

        # Buttons
        button_layout = QHBoxLayout()
        add_button = QPushButton("Add Book")
        add_button.clicked.connect(self.add_book)
        edit_button = QPushButton("Edit Book")
        edit_button.clicked.connect(self.edit_book)
        delete_button = QPushButton("Delete Book")
        delete_button.clicked.connect(self.delete_book)
        clear_button = QPushButton("Clear Fields")
        clear_button.clicked.connect(self.clear_fields)

        # Style buttons
        for button in [add_button, edit_button, delete_button, clear_button]:
            button.setMinimumWidth(120)
            button.setStyleSheet("""
                QPushButton {
                    padding: 5px 15px;
                    border-radius: 3px;
                    font-weight: bold;
                }
            """)

        add_button.setStyleSheet(add_button.styleSheet() + "background-color: #4CAF50; color: white;")
        edit_button.setStyleSheet(edit_button.styleSheet() + "background-color: #008CBA; color: white;")
        delete_button.setStyleSheet(delete_button.styleSheet() + "background-color: #f44336; color: white;")

        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(clear_button)

        layout.addWidget(self.book_table)
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)

        # Load books
        self.load_books()

    def load_books(self):
        try:
            connection = create_db_connection()
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT b.*, u.username 
                    FROM books b 
                    LEFT JOIN users u ON b.issuer_id = u.id
                """)
                books = cursor.fetchall()

                self.book_table.setRowCount(len(books))
                for i, book in enumerate(books):
                    # Display book details
                    self.book_table.setItem(i, 0, QTableWidgetItem(book[1]))  # Title
                    self.book_table.setItem(i, 1, QTableWidgetItem(book[2]))  # Book ID
                    self.book_table.setItem(i, 2, QTableWidgetItem(book[3]))  # Author
                    self.book_table.setItem(i, 3, QTableWidgetItem(book[4]))  # Status
                    self.book_table.setItem(i, 4, QTableWidgetItem(str(book[-1] or '')))  # Issuer username
                    self.book_table.setItem(i, 5, QTableWidgetItem(book[6]))  # Course Code
                    due_date = book[8].strftime('%Y-%m-%d') if book[8] else ''
                    self.book_table.setItem(i, 6, QTableWidgetItem(due_date))  # Due Date

                    # Add return button for issued books
                    if book[4] == 'Issued':
                        return_button = QPushButton("Return Book")
                        return_button.setStyleSheet("""
                            QPushButton {
                                background-color: #FF9800;
                                color: white;
                                padding: 3px 8px;
                                border-radius: 2px;
                            }
                            QPushButton:hover {
                                background-color: #F57C00;
                            }
                        """)
                        return_button.clicked.connect(lambda checked, bid=book[2]: self.return_book(bid))
                        self.book_table.setCellWidget(i, 7, return_button)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load books: {str(e)}")
        finally:
            if 'connection' in locals():
                connection.close()
    def return_book(self, book_id):
        try:
            connection = create_db_connection()
            with connection.cursor() as cursor:
                # Get current book status and issuer
                cursor.execute("""
                    SELECT status, issuer_id 
                    FROM books 
                    WHERE book_id = %s
                """, (book_id,))
                book_info = cursor.fetchone()
                
                if not book_info or book_info[0] != 'Issued':
                    QMessageBox.warning(self, "Error", "This book is not currently issued")
                    return

                reply = QMessageBox.question(
                    self,
                    "Confirm Return",
                    "Are you sure you want to mark this book as returned?",
                    QMessageBox.Yes | QMessageBox.No
                )

                if reply == QMessageBox.Yes:
                    # Update book status
                    cursor.execute("""
                        UPDATE books 
                        SET status = 'Available',
                            issuer_id = NULL,
                            issue_date = NULL,
                            return_date = NULL
                        WHERE book_id = %s
                    """, (book_id,))

                    # Update user's issued books count
                    cursor.execute("""
                        UPDATE users 
                        SET books_issued = books_issued - 1 
                        WHERE id = %s
                    """, (book_info[1],))

                    # Update any related book request status
                    cursor.execute("""
                        UPDATE book_requests 
                        SET status = 'Returned' 
                        WHERE book_id = %s AND status = 'Approved'
                    """, (book_id,))

                    connection.commit()
                    QMessageBox.information(self, "Success", "Book has been marked as returned!")
                    self.load_books()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to process return: {str(e)}")
            if 'connection' in locals():
                connection.rollback()
        finally:
            if 'connection' in locals():
                connection.close()

    def book_selected(self, item):
        row = item.row()
        self.selected_book = {
            'title': self.book_table.item(row, 0).text(),
            'book_id': self.book_table.item(row, 1).text(),
            'author': self.book_table.item(row, 2).text(),
            'status': self.book_table.item(row, 3).text(),
            'course_code': self.book_table.item(row, 5).text()
        }

        # Fill the form with selected book's data
        self.title_input.setText(self.selected_book['title'])
        self.book_id_input.setText(self.selected_book['book_id'])
        self.author_input.setText(self.selected_book['author'])
        self.status_combo.setCurrentText(self.selected_book['status'])
        self.course_code_input.setText(self.selected_book['course_code'])

    def add_book(self):
        if not self.book_id_input.text():
            QMessageBox.warning(self, "Error", "Book ID is required")
            return

        try:
            connection = create_db_connection()
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO books (title, book_id, author, status, course_code)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    self.title_input.text(),
                    self.book_id_input.text(),
                    self.author_input.text(),
                    self.status_combo.currentText(),
                    self.course_code_input.text()
                ))
                connection.commit()
                QMessageBox.information(self, "Success", "Book added successfully!")
                self.clear_fields()
                self.load_books()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add book: {str(e)}")
        finally:
            if 'connection' in locals():
                connection.close()

    def edit_book(self):
        if not self.selected_book:
            QMessageBox.warning(self, "Error", "Please select a book to edit")
            return

        try:
            connection = create_db_connection()
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE books
                    SET title = %s, author = %s, status = %s, course_code = %s
                    WHERE book_id = %s
                """, (
                    self.title_input.text(),
                    self.author_input.text(),
                    self.status_combo.currentText(),
                    self.course_code_input.text(),
                    self.selected_book['book_id']
                ))
                connection.commit()
                QMessageBox.information(self, "Success", "Book updated successfully!")
                self.clear_fields()
                self.load_books()
                self.selected_book = None
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update book: {str(e)}")
        finally:
            if 'connection' in locals():
                connection.close()

    def delete_book(self):
        if not self.selected_book:
            QMessageBox.warning(self, "Error", "Please select a book to delete")
            return

        try:
            connection = create_db_connection()
            with connection.cursor() as cursor:
                # Check if book has any active issues
                if self.selected_book['status'] == 'Issued':
                    QMessageBox.warning(
                        self, 
                        "Cannot Delete", 
                        "This book is currently issued. Please wait for it to be returned."
                    )
                    return

                # Check for pending requests
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM book_requests 
                    WHERE book_id = %s AND status = 'Pending'
                """, (self.selected_book['book_id'],))
                
                pending_requests = cursor.fetchone()[0]
                if pending_requests > 0:
                    reply = QMessageBox.question(
                        self,
                        "Pending Requests",
                        f"This book has {pending_requests} pending request(s). Delete anyway?",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    if reply == QMessageBox.No:
                        return

                reply = QMessageBox.question(
                    self,
                    "Confirm Delete",
                    "Are you sure you want to delete this book?",
                    QMessageBox.Yes | QMessageBox.No
                )

                if reply == QMessageBox.Yes:
                    # Delete related requests first
                    cursor.execute(
                        "DELETE FROM book_requests WHERE book_id = %s",
                        (self.selected_book['book_id'],)
                    )
                    
                    # Then delete the book
                    cursor.execute(
                        "DELETE FROM books WHERE book_id = %s",
                        (self.selected_book['book_id'],)
                    )
                    
                    connection.commit()
                    QMessageBox.information(self, "Success", "Book deleted successfully!")
                    self.clear_fields()
                    self.load_books()
                    self.selected_book = None

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete book: {str(e)}")
            if 'connection' in locals():
                connection.rollback()
        finally:
            if 'connection' in locals():
                connection.close()

    def clear_fields(self):
        self.title_input.clear()
        self.book_id_input.clear()
        self.author_input.clear()
        self.status_combo.setCurrentIndex(0)
        self.course_code_input.clear()
        self.selected_book = None
class AdminPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)  # Properly pass parent to super
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # User management section
        user_group = QGroupBox("User Management")
        user_layout = QVBoxLayout()

        # User list
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(6)
        self.user_table.setHorizontalHeaderLabels([
            "ID", "Username", "Is Admin", "Book Limit", "Books Issued", "Actions"
        ])
        # Enable selection of entire rows
        self.user_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.user_table.setSelectionMode(QTableWidget.SingleSelection)

        # Add user section with grouped controls
        add_user_group = QGroupBox("Add New User")
        add_user_layout = QGridLayout()

        # Create input fields
        self.new_username = QLineEdit()
        self.new_username.setPlaceholderText("Username")
        self.new_password = QLineEdit()
        self.new_password.setPlaceholderText("Password")
        self.is_admin_check = QCheckBox("Is Admin")
        
        self.book_limit_spin = QSpinBox()
        self.book_limit_spin.setRange(1, 10)
        self.book_limit_spin.setValue(3)
        self.book_limit_spin.setPrefix("Book Limit: ")

        # Create buttons with styling
        add_button = QPushButton("Add User")
        add_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        add_button.clicked.connect(self.add_user)

        delete_button = QPushButton("Delete Selected User")
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        delete_button.clicked.connect(self.delete_user)

        # Arrange input fields in grid
        add_user_layout.addWidget(QLabel("Username:"), 0, 0)
        add_user_layout.addWidget(self.new_username, 0, 1)
        add_user_layout.addWidget(QLabel("Password:"), 1, 0)
        add_user_layout.addWidget(self.new_password, 1, 1)
        add_user_layout.addWidget(self.is_admin_check, 2, 0)
        add_user_layout.addWidget(self.book_limit_spin, 2, 1)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(add_button)
        button_layout.addWidget(delete_button)
        add_user_layout.addLayout(button_layout, 3, 0, 1, 2)

        add_user_group.setLayout(add_user_layout)

        # Add all components to main layout
        user_layout.addWidget(self.user_table)
        user_layout.addWidget(add_user_group)
        user_group.setLayout(user_layout)
        main_layout.addWidget(user_group)

        self.load_users()

    def delete_user(self):
        selected_items = self.user_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Error", "Please select a user to delete")
            return

        user_id = int(self.user_table.item(selected_items[0].row(), 0).text())
        username = self.user_table.item(selected_items[0].row(), 1).text()

        if username == "admin":
            QMessageBox.warning(self, "Error", "Cannot delete admin user")
            return

        reply = QMessageBox.question(self, 'Delete User', 
                                   f'Are you sure you want to delete user "{username}"?',
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                connection = create_db_connection()
                with connection.cursor() as cursor:
                    # First delete any book requests by this user
                    cursor.execute("DELETE FROM book_requests WHERE user_id = %s", (user_id,))
                    # Then delete the user
                    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
                    connection.commit()
                self.load_users()
                QMessageBox.information(self, "Success", "User deleted successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete user: {str(e)}")
            finally:
                if 'connection' in locals():
                    connection.close()

    def load_users(self):
        try:
            connection = create_db_connection()
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, username, is_admin, book_limit, books_issued FROM users")
                users = cursor.fetchall()
                
                self.user_table.setRowCount(len(users))
                for i, user in enumerate(users):
                    self.user_table.setItem(i, 0, QTableWidgetItem(str(user[0])))
                    self.user_table.setItem(i, 1, QTableWidgetItem(user[1]))
                    self.user_table.setItem(i, 2, QTableWidgetItem("Yes" if user[2] else "No"))
                    self.user_table.setItem(i, 3, QTableWidgetItem(str(user[3] if user[3] is not None else "N/A")))
                    self.user_table.setItem(i, 4, QTableWidgetItem(str(user[4] if user[4] is not None else 0)))
                    
                    if not user[2]:  # If not admin
                        edit_limit_btn = QPushButton("Edit Limit")
                        edit_limit_btn.setStyleSheet("""
                            QPushButton {
                                background-color: #008CBA;
                                color: white;
                                padding: 3px 10px;
                                border-radius: 2px;
                            }
                            QPushButton:hover {
                                background-color: #007399;
                            }
                        """)
                        edit_limit_btn.clicked.connect(lambda checked, u_id=user[0]: self.edit_book_limit(u_id))
                        self.user_table.setCellWidget(i, 5, edit_limit_btn)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load users: {str(e)}")
        finally:
            if 'connection' in locals():
                connection.close()

    def add_user(self):
        username = self.new_username.text()
        password = self.new_password.text()
        is_admin = self.is_admin_check.isChecked()
        book_limit = self.book_limit_spin.value()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Username and password are required")
            return

        try:
            connection = create_db_connection()
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO users (username, password, is_admin, book_limit) VALUES (%s, %s, %s, %s)",
                    (username, password, is_admin, book_limit if not is_admin else None)
                )
                connection.commit()
            
            self.load_users()
            self.new_username.clear()
            self.new_password.clear()
            self.is_admin_check.setChecked(False)
            self.book_limit_spin.setValue(3)
            QMessageBox.information(self, "Success", "User added successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add user: {str(e)}")
        finally:
            if 'connection' in locals():
                connection.close()

    def edit_book_limit(self, user_id):
        try:
            connection = create_db_connection()
            with connection.cursor() as cursor:
                cursor.execute("SELECT book_limit FROM users WHERE id = %s", (user_id,))
                current_limit = cursor.fetchone()[0]
                
                new_limit, ok = QInputDialog.getInt(
                    self, "Edit Book Limit", 
                    "Enter new book limit:",
                    value=current_limit,
                    min=1, max=10
                )
                
                if ok:
                    cursor.execute(
                        "UPDATE users SET book_limit = %s WHERE id = %s",
                        (new_limit, user_id)
                    )
                    connection.commit()
                    self.load_users()
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update book limit: {str(e)}")
        finally:
            if 'connection' in locals():
                connection.close()
                
class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setModal(True)
        self.setup_ui()
        self.is_authenticated = False
        self.user_data = None

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Username field
        username_layout = QHBoxLayout()
        username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)

        # Password field
        password_layout = QHBoxLayout()
        password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)

        # Login button
        login_button = QPushButton("Login")
        login_button.clicked.connect(self.handle_login)

        # Exit button
        exit_button = QPushButton("Exit")
        exit_button.clicked.connect(self.handle_exit)
        exit_button.setStyleSheet("background-color: #f44336; color: white;")

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(login_button)
        button_layout.addWidget(exit_button)

        # Add to main layout
        layout.addLayout(username_layout)
        layout.addLayout(password_layout)
        layout.addLayout(button_layout)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        try:
            connection = create_db_connection()
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM users WHERE username = %s AND password = %s",
                    (username, password)
                )
                user = cursor.fetchone()
                
                if user:
                    self.user_data = type('User', (), {
                        'id': user[0],
                        'username': user[1],
                        'password': user[2],
                        'is_admin': user[3]
                    })
                    self.is_authenticated = True
                    self.accept()
                else:
                    QMessageBox.warning(self, "Login Failed", "Invalid username or password")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Login failed: {str(e)}")
        finally:
            if 'connection' in locals():
                connection.close()

    def handle_exit(self):
        self.reject()
        sys.exit()

class LibraryApp(QMainWindow):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.is_admin = user_data.is_admin
        self.setWindowTitle("Library Management System")
        self.setGeometry(100, 100, 1200, 800)
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create toolbar
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Add user info and logout button to toolbar
        user_layout = QHBoxLayout()
        user_label = QLabel(f"Logged in as: {self.user_data.username}")
        logout_button = QPushButton("Logout")
        logout_button.clicked.connect(self.logout)
        logout_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 5px 15px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        
        # Create a widget to hold the horizontal layout
        toolbar_widget = QWidget()
        toolbar_layout = QHBoxLayout(toolbar_widget)
        toolbar_layout.addWidget(user_label)
        toolbar_layout.addWidget(logout_button)
        toolbar_layout.setContentsMargins(5, 0, 5, 0)
        toolbar_widget.setLayout(toolbar_layout)
        
        toolbar.addWidget(toolbar_widget)

        # Create main content area with tabs
        tabs = QTabWidget()
        layout.addWidget(tabs)

        # Add tabs
        tabs.addTab(BookListWidget(self.user_data), "Book Inventory")
        if self.is_admin:
            tabs.addTab(ManageBooksWidget(), "Manage Books")
            tabs.addTab(RequestManagementWidget(self), "Manage Requests")
            tabs.addTab(AdminPanel(self), "Admin Panel")

    def logout(self):
        reply = QMessageBox.question(self, 'Logout', 
                                   'Are you sure you want to logout?',
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.hide()  # Hide current window instead of closing
            self.show_login()

    def show_login(self):
        login = LoginDialog()
        if login.exec_() == QDialog.Accepted and login.is_authenticated:
            self.close()  # Close the old window
            new_window = LibraryApp(login.user_data)
            new_window.show()
        else:
            self.close()  # Close the application if login is cancelled
            sys.exit()  
class RequestManagementWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Filter options
        filter_layout = QHBoxLayout()
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Pending Requests", "Request History"])
        self.filter_combo.currentTextChanged.connect(self.load_requests)
        filter_layout.addWidget(QLabel("View:"))
        filter_layout.addWidget(self.filter_combo)
        filter_layout.addStretch()

        # Statistics section
        stats_group = QGroupBox("Request Statistics")
        stats_layout = QHBoxLayout()
        self.pending_count = QLabel("Pending: 0")
        self.approved_count = QLabel("Approved: 0")
        self.rejected_count = QLabel("Rejected: 0")
        stats_layout.addWidget(self.pending_count)
        stats_layout.addWidget(self.approved_count)
        stats_layout.addWidget(self.rejected_count)
        stats_group.setLayout(stats_layout)

        # Requests table
        self.requests_table = QTableWidget()
        self.requests_table.setColumnCount(9)
        self.requests_table.setHorizontalHeaderLabels([
            "Request ID", "Book Title", "Book ID", "Student Name",
            "Request Date", "Status", "Books Issued", "Available Limit", "Actions"
        ])
        
        # Set column widths
        self.requests_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        
        # Add components to main layout
        layout.addLayout(filter_layout)
        layout.addWidget(stats_group)
        layout.addWidget(self.requests_table)

        # Load initial data
        self.load_requests()
        self.update_statistics()

    def load_requests(self):
        try:
            view_type = self.filter_combo.currentText()
            connection = create_db_connection()
            with connection.cursor() as cursor:
                query = """
                    SELECT 
                        br.id,
                        b.title,
                        b.book_id,
                        u.username,
                        br.request_date,
                        br.status,
                        u.books_issued,
                        u.book_limit,
                        u.id as user_id
                    FROM book_requests br
                    JOIN books b ON br.book_id = b.book_id
                    JOIN users u ON br.user_id = u.id
                """
                
                if view_type == "Pending Requests":
                    cursor.execute(query + " WHERE br.status = 'Pending' ORDER BY br.request_date DESC")
                else:  # Request History
                    cursor.execute(query + " WHERE br.status != 'Pending' ORDER BY br.request_date DESC")
                
                requests = cursor.fetchall()
                
                self.requests_table.setRowCount(len(requests))
                for i, req in enumerate(requests):
                    # Request ID
                    self.requests_table.setItem(i, 0, QTableWidgetItem(str(req[0])))
                    # Book Title
                    self.requests_table.setItem(i, 1, QTableWidgetItem(req[1]))
                    # Book ID
                    self.requests_table.setItem(i, 2, QTableWidgetItem(req[2]))
                    # Student Name
                    self.requests_table.setItem(i, 3, QTableWidgetItem(req[3]))
                    # Request Date
                    request_date = req[4].strftime('%Y-%m-%d %H:%M') if req[4] else ""
                    self.requests_table.setItem(i, 4, QTableWidgetItem(request_date))
                    # Status
                    self.requests_table.setItem(i, 5, QTableWidgetItem(req[5]))
                    # Books Issued
                    self.requests_table.setItem(i, 6, QTableWidgetItem(str(req[6])))
                    # Available Limit
                    remaining_limit = req[7] - req[6]
                    self.requests_table.setItem(i, 7, QTableWidgetItem(f"{remaining_limit}/{req[7]}"))
                    
                    # Action buttons for pending requests
                    if view_type == "Pending Requests":
                        action_widget = QWidget()
                        action_layout = QHBoxLayout(action_widget)
                        action_layout.setContentsMargins(2, 2, 2, 2)
                        
                        if req[6] < req[7]:  # If user hasn't reached their limit
                            approve_btn = QPushButton("Approve")
                            approve_btn.setStyleSheet("background-color: #4CAF50; color: white;")
                            approve_btn.clicked.connect(
                                lambda checked, rid=req[0], bid=req[2], uid=req[8]: 
                                self.handle_request(rid, bid, uid, "Approved")
                            )
                            action_layout.addWidget(approve_btn)
                        
                        reject_btn = QPushButton("Reject")
                        reject_btn.setStyleSheet("background-color: #f44336; color: white;")
                        reject_btn.clicked.connect(
                            lambda checked, rid=req[0], bid=req[2], uid=req[8]: 
                            self.handle_request(rid, bid, uid, "Rejected")
                        )
                        
                        action_layout.addWidget(reject_btn)
                        self.requests_table.setCellWidget(i, 8, action_widget)
                    else:
                        self.requests_table.setItem(i, 8, QTableWidgetItem(req[5]))

            self.update_statistics()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load requests: {str(e)}")
        finally:
            if 'connection' in locals():
                connection.close()

    def update_statistics(self):
        try:
            connection = create_db_connection()
            with connection.cursor() as cursor:
                # Get counts for different statuses
                cursor.execute("""
                    SELECT status, COUNT(*) 
                    FROM book_requests 
                    GROUP BY status
                """)
                stats = dict(cursor.fetchall())
                
                self.pending_count.setText(f"Pending: {stats.get('Pending', 0)}")
                self.approved_count.setText(f"Approved: {stats.get('Approved', 0)}")
                self.rejected_count.setText(f"Rejected: {stats.get('Rejected', 0)}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update statistics: {str(e)}")
        finally:
            if 'connection' in locals():
                connection.close()

    def handle_request(self, request_id, book_id, user_id, status):
        try:
            connection = create_db_connection()
            with connection.cursor() as cursor:
                if status == "Approved":
                    # Check user's current book count and limit
                    cursor.execute("""
                        SELECT books_issued, book_limit 
                        FROM users 
                        WHERE id = %s
                    """, (user_id,))
                    books_issued, book_limit = cursor.fetchone()
                    
                    if books_issued >= book_limit:
                        QMessageBox.warning(
                            self, 
                            "Limit Exceeded", 
                            f"User has reached their book limit ({book_limit} books)"
                        )
                        return
                    
                    # Update books issued count
                    cursor.execute("""
                        UPDATE users 
                        SET books_issued = books_issued + 1 
                        WHERE id = %s
                    """, (user_id,))
                    
                    # Update book status
                    cursor.execute("""
                        UPDATE books 
                        SET status = 'Issued', 
                            issuer_id = %s,
                            issue_date = NOW(),
                            return_date = DATE_ADD(NOW(), INTERVAL 14 DAY)
                        WHERE book_id = %s
                    """, (user_id, book_id))

                # Update request status
                cursor.execute("""
                    UPDATE book_requests 
                    SET status = %s, 
                        approval_date = NOW() 
                    WHERE id = %s
                """, (status, request_id))

                connection.commit()
                QMessageBox.information(
                    self, 
                    "Success", 
                    f"Request {status.lower()} successfully!"
                )
                self.load_requests()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to process request: {str(e)}")
        finally:
            if 'connection' in locals():
                connection.close()

                
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Set dark theme palette
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Text, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))

    app.setPalette(dark_palette)

    while True:
        login = LoginDialog()
        if login.exec_() == QDialog.Accepted and login.is_authenticated:
            window = LibraryApp(login.user_data)
            window.show()
            app.exec_()
        else:
            break

    sys.exit()

if __name__ == '__main__':
    main()