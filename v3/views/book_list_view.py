from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                            QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                            QComboBox, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from components.glass_card import GlassCard
from components.action_button import ActionButton
from database.book_dao import BookDAO
from database.request_dao import BookRequestDAO
from models.book_request import BookRequest

class BookListWidget(QWidget):
    def __init__(self, user=None):
        super().__init__()
        self.user = user
        self.setup_ui()
        self.load_books()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header and search section
        header_card = GlassCard()
        header_layout = QVBoxLayout(header_card)

        title_label = QLabel("Book Library")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")

        # Search and filter section
        search_layout = QHBoxLayout()
        search_layout.setSpacing(15)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search books by title, ID, author, or course...")
        self.search_input.setMinimumHeight(38)

        search_button = ActionButton("Search", ActionButton.STYLE_PRIMARY)
        search_button.setIcon(QIcon("./assets/images/search_icon.png"))
        search_button.clicked.connect(self.search_books)

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Books", "Available Books", "My Requests"])
        self.filter_combo.setMinimumHeight(38)
        self.filter_combo.currentTextChanged.connect(self.filter_books)

        search_layout.addWidget(self.search_input, 7)
        search_layout.addWidget(search_button, 1)
        search_layout.addWidget(self.filter_combo, 2)

        header_layout.addWidget(title_label)
        header_layout.addLayout(search_layout)

        # Book table
        table_card = GlassCard()
        table_layout = QVBoxLayout(table_card)

        self.book_table = QTableWidget()
        self.book_table.setColumnCount(8)
        self.book_table.setHorizontalHeaderLabels([
            "Title", "Book ID", "Author", "Status",
            "Issuer", "Course Code", "Due Date", "Action"
        ])

        # Adjust column widths
        self.book_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.book_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

        self.book_table.setAlternatingRowColors(True)
        self.book_table.verticalHeader().setVisible(False)

        table_layout.addWidget(self.book_table)

        # Add everything to main layout
        layout.addWidget(header_card, 1)
        layout.addWidget(table_card, 5)

    def load_books(self):
        try:
            books = BookDAO.get_books_with_request_status(self.user.id if self.user else None)
            self.update_table(books)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load books: {str(e)}")

    def search_books(self):
        search_text = self.search_input.text()
        try:
            books = BookDAO.search_books(search_text, self.user.id if self.user else None)
            self.update_table(books)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Search failed: {str(e)}")

    def filter_books(self):
        filter_option = self.filter_combo.currentText()
        try:
            books = BookDAO.filter_books(filter_option, self.user.id if self.user else None)
            self.update_table(books)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Filter failed: {str(e)}")

    def request_book(self, book_id):
        try:
            # Create a book request
            request = BookRequest(
                book_id=book_id,
                user_id=self.user.id,
                status="Pending"
            )
            
            BookRequestDAO.create_request(request)
            
            # Log the activity
            from database.activity_dao import ActivityDAO
            book = BookDAO.get_book_by_id(book_id)
            ActivityDAO.log_activity(
                self.user.id, 
                "request", 
                "book", 
                book_id, 
                f"Requested book: {book.title if book else book_id}"
            )
            
            QMessageBox.information(self, "Success", "Book request submitted successfully!")
            self.load_books()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to request book: {str(e)}")

    def update_table(self, books):
        self.book_table.setRowCount(len(books))
        for i, book in enumerate(books):
            # Fill in the book data
            self.book_table.setItem(i, 0, QTableWidgetItem(book[1]))  # Title
            self.book_table.setItem(i, 1, QTableWidgetItem(book[2]))  # Book ID
            self.book_table.setItem(i, 2, QTableWidgetItem(book[3] or ""))  # Author
            self.book_table.setItem(i, 3, QTableWidgetItem(book[4]))  # Status

            # Issuer name (from join with users)
            issuer = book[10] if len(book) > 10 else ""
            self.book_table.setItem(i, 4, QTableWidgetItem(issuer or ""))

            self.book_table.setItem(i, 5, QTableWidgetItem(book[6] or ""))  # Course Code

            # Due date (return date)
            due_date = book[8].strftime('%Y-%m-%d') if book[8] else ""
            self.book_table.setItem(i, 6, QTableWidgetItem(due_date))

            # Add action button if user is logged in and not admin
            if self.user and not self.user.is_admin:
                # Get request status
                request_status = book[9] if len(book) > 9 else None

                # Create appropriate button based on book status and request status
                action_button = ActionButton()

                if book[4] == "Available":  # If book is available
                    if request_status == "Pending":
                        action_button.setText("Pending")
                        action_button.setEnabled(False)
                    elif request_status == "Approved":
                        action_button.setText("Approved")
                        action_button.setEnabled(False)
                    else:
                        action_button.setText("Request")
                        action_button.clicked.connect(lambda checked, bid=book[2]: self.request_book(bid))
                else:
                    action_button.setText("Not Available")
                    action_button.setEnabled(False)

                self.book_table.setCellWidget(i, 7, action_button)
