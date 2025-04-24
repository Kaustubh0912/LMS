from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                            QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                            QComboBox, QMessageBox, QFormLayout, QGroupBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from components.glass_card import GlassCard
from components.action_button import ActionButton
from database.book_dao import BookDAO
from models.book import Book
from utils.resources import get_icon

class ManageBooksWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_book = None
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Search section at the top
        search_card = GlassCard()
        search_layout = QHBoxLayout(search_card)
        
        search_label = QLabel("Search Books:")
        search_label.setStyleSheet("color: white; font-weight: bold;")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter title, ID, author or course code...")
        self.search_input.setMinimumHeight(35)
        self.search_input.returnPressed.connect(self.search_books)
        
        search_button = ActionButton("Search")
        search_button.setIcon(get_icon("./assets/images/search_icon.png", "S"))
        search_button.clicked.connect(self.search_books)
        
        clear_search = ActionButton("Clear", ActionButton.STYLE_WARNING)
        clear_search.clicked.connect(self.clear_search)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input, 1)  # Add stretch factor 1
        search_layout.addWidget(search_button)
        search_layout.addWidget(clear_search)
        
        # Book table for displaying books
        table_card = GlassCard()
        table_layout = QVBoxLayout(table_card)

        table_header = QLabel("Library Books")
        table_header.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")

        self.book_table = QTableWidget()
        self.book_table.setColumnCount(8)  # Added a column for return button
        self.book_table.setHorizontalHeaderLabels([
            "Title", "Book ID", "Author", "Status",
            "Issuer", "Course Code", "Due Date", "Actions"
        ])
        self.book_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.book_table.setSelectionMode(QTableWidget.SingleSelection)
        self.book_table.itemClicked.connect(self.book_selected)
        self.book_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.book_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.book_table.setAlternatingRowColors(True)
        self.book_table.verticalHeader().setVisible(False)

        table_layout.addWidget(table_header)
        table_layout.addWidget(self.book_table)

        # Book form for adding/editing books
        form_card = GlassCard()
        form_layout = QVBoxLayout(form_card)

        form_header = QLabel("Book Details")
        form_header.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")

        detail_form = QFormLayout()
        detail_form.setVerticalSpacing(15)
        detail_form.setHorizontalSpacing(20)

        self.title_input = QLineEdit()
        self.book_id_input = QLineEdit()
        self.author_input = QLineEdit()
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Available", "Issued"])
        self.course_code_input = QLineEdit()

        # Set minimum height for form controls
        for widget in [self.title_input, self.book_id_input, self.author_input,
                       self.status_combo, self.course_code_input]:
            widget.setMinimumHeight(35)

        detail_form.addRow("Title:", self.title_input)
        detail_form.addRow("Book ID:", self.book_id_input)
        detail_form.addRow("Author:", self.author_input)
        detail_form.addRow("Status:", self.status_combo)
        detail_form.addRow("Course Code:", self.course_code_input)

        # Buttons for book operations
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        add_button = ActionButton("Add Book", ActionButton.STYLE_SUCCESS)
        add_button.clicked.connect(self.add_book)
        add_button.setIcon(get_icon("./assets/images/add_icon.png", "+"))

        edit_button = ActionButton("Edit Book", ActionButton.STYLE_PRIMARY)
        edit_button.clicked.connect(self.edit_book)
        edit_button.setIcon(get_icon("./assets/images/edit_icon.png", "E"))

        delete_button = ActionButton("Delete Book", ActionButton.STYLE_DANGER)
        delete_button.clicked.connect(self.delete_book)
        delete_button.setIcon(get_icon("./assets/images/delete_icon.png", "D"))

        clear_button = ActionButton("Clear Fields")
        clear_button.clicked.connect(self.clear_fields)
        clear_button.setIcon(get_icon("./assets/images/clear_icon.png", "C"))

        buttons_layout.addWidget(add_button)
        buttons_layout.addWidget(edit_button)
        buttons_layout.addWidget(delete_button)
        buttons_layout.addWidget(clear_button)

        form_layout.addWidget(form_header)
        form_layout.addLayout(detail_form)
        form_layout.addLayout(buttons_layout)

        # Add everything to main layout
        main_layout.addWidget(search_card)  # Add search at top
        main_layout.addWidget(table_card, 3)
        main_layout.addWidget(form_card, 2)

        # Load books
        self.load_books()
        
    def search_books(self):
        search_text = self.search_input.text().strip()
        if not search_text:
            self.load_books()  # Load all books if search is empty
            return
            
        try:
            books = BookDAO.search_books(search_text)
            
            if not books or len(books) == 0:
                QMessageBox.information(self, "Search Results", "No books found matching your search criteria.")
                return
                
            self.update_book_table(books)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Search failed: {str(e)}")
    
    def clear_search(self):
        self.search_input.clear()
        self.load_books()
    
    def update_book_table(self, books):
        self.book_table.setRowCount(len(books))
        for i, book in enumerate(books):
            # Display book details
            self.book_table.setItem(i, 0, QTableWidgetItem(book[1]))  # Title
            self.book_table.setItem(i, 1, QTableWidgetItem(book[2]))  # Book ID
            self.book_table.setItem(i, 2, QTableWidgetItem(book[3] or ""))  # Author
            self.book_table.setItem(i, 3, QTableWidgetItem(book[4]))  # Status

            # Issuer name (from join)
            issuer = book[10] if len(book) > 10 else ""
            self.book_table.setItem(i, 4, QTableWidgetItem(issuer or ""))

            self.book_table.setItem(i, 5, QTableWidgetItem(book[6] or ""))  # Course Code

            # Due date
            due_date = book[8].strftime('%Y-%m-%d') if book[8] else ""
            self.book_table.setItem(i, 6, QTableWidgetItem(due_date))

            # Add return button for issued books
            if book[4] == 'Issued':
                return_button = ActionButton("Return Book", ActionButton.STYLE_WARNING)
                return_button.clicked.connect(lambda checked, bid=book[2]: self.return_book(bid))
                self.book_table.setCellWidget(i, 7, return_button)

    def load_books(self):
        try:
            books = BookDAO.get_books_with_request_status()
            self.update_book_table(books)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load books: {str(e)}")

    def return_book(self, book_id):
        try:
            print(f"Attempting to return book with ID: {book_id}")
            
            # Verify book exists and get current status
            book = BookDAO.get_book_by_id(book_id)
            if not book:
                print(f"Book with ID {book_id} not found in database")
                QMessageBox.warning(self, "Error", "Book not found in the database.")
                return
                
            print(f"Current book status: {book.status}, Issuer ID: {book.issuer_id}")
            
            if book.status != "Issued":
                QMessageBox.warning(self, "Error", f"This book is not currently issued (Status: {book.status}).")
                return
                
            if not book.issuer_id:
                QMessageBox.warning(self, "Error", "This book has no recorded issuer.")
                return

            reply = QMessageBox.question(
                self,
                "Confirm Return",
                f"Are you sure you want to mark the book '{book.title}' as returned?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                print(f"User confirmed return of book: {book_id}")
                result = BookDAO.return_book(book_id)
                print(f"Return book operation result: {result}")
                
                if result:
                    QMessageBox.information(self, "Success", "Book has been marked as returned!")
                    self.load_books()
                else:
                    QMessageBox.warning(self, "Error", "Failed to return book. See console for details.")
        except Exception as e:
            print(f"Exception in return_book method: {e}")
            QMessageBox.critical(self, "Error", f"Failed to process return: {str(e)}")

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
            book = Book(
                title=self.title_input.text(),
                book_id=self.book_id_input.text(),
                author=self.author_input.text(),
                status=self.status_combo.currentText(),
                course_code=self.course_code_input.text()
            )

            if BookDAO.add_book(book):
                QMessageBox.information(self, "Success", "Book added successfully!")
                self.clear_fields()
                self.load_books()
            else:
                QMessageBox.warning(self, "Error", "Failed to add book")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add book: {str(e)}")
    def edit_book(self):
        if not self.selected_book:
            QMessageBox.warning(self, "Error", "Please select a book to edit")
            return

        try:
            book = Book(
                title=self.title_input.text(),
                book_id=self.selected_book['book_id'],  # Keep original book_id
                author=self.author_input.text(),
                status=self.status_combo.currentText(),
                course_code=self.course_code_input.text()
            )

            if BookDAO.update_book(book):
                QMessageBox.information(self, "Success", "Book updated successfully!")
                self.clear_fields()
                self.load_books()
                self.selected_book = None
            else:
                QMessageBox.warning(self, "Error", "Failed to update book")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update book: {str(e)}")

    def delete_book(self):
        if not self.selected_book:
            QMessageBox.warning(self, "Error", "Please select a book to delete")
            return

        try:
            # Confirm deletion
            reply = QMessageBox.question(
                self,
                "Confirm Delete",
                f"Are you sure you want to delete the book '{self.selected_book['title']}'?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                if BookDAO.delete_book(self.selected_book['book_id']):
                    QMessageBox.information(self, "Success", "Book deleted successfully!")
                    self.clear_fields()
                    self.load_books()
                    self.selected_book = None
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete book")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete book: {str(e)}")

    def clear_fields(self):
        self.title_input.clear()
        self.book_id_input.clear()
        self.author_input.clear()
        self.status_combo.setCurrentIndex(0)
        self.course_code_input.clear()
        self.selected_book = None
