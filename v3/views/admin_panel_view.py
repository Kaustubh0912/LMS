from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                             QCheckBox, QSpinBox, QMessageBox, QInputDialog, QGroupBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont
from components.glass_card import GlassCard
from components.action_button import ActionButton
from database.user_dao import UserDAO
from models.user import User

class AdminPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # User Management Section
        user_card = GlassCard()
        user_layout = QVBoxLayout(user_card)

        title_label = QLabel("User Management")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")

        # User Table
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(6)
        self.user_table.setHorizontalHeaderLabels([
            "ID", "Username", "Is Admin", "Book Limit", "Books Issued", "Actions"
        ])

        # Set table properties
        self.user_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.user_table.setSelectionMode(QTableWidget.SingleSelection)
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.user_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.user_table.setAlternatingRowColors(True)
        self.user_table.verticalHeader().setVisible(False)

        user_layout.addWidget(title_label)
        user_layout.addWidget(self.user_table)

        # Add New User Section
        add_user_card = GlassCard()
        add_user_layout = QVBoxLayout(add_user_card)

        add_title = QLabel("Add New User")
        add_title.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")

        # Form layout in grid
        form_layout = QHBoxLayout()

        # Username and password fields
        credentials_layout = QVBoxLayout()

        username_layout = QVBoxLayout()
        username_label = QLabel("Username:")
        username_label.setStyleSheet("color: white; font-weight: bold;")
        self.new_username = QLineEdit()
        self.new_username.setPlaceholderText("Enter username")
        self.new_username.setMinimumHeight(35)
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.new_username)

        password_layout = QVBoxLayout()
        password_label = QLabel("Password:")
        password_label.setStyleSheet("color: white; font-weight: bold;")
        self.new_password = QLineEdit()
        self.new_password.setPlaceholderText("Enter password")
        self.new_password.setMinimumHeight(35)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.new_password)

        credentials_layout.addLayout(username_layout)
        credentials_layout.addLayout(password_layout)

        # User settings
        settings_layout = QVBoxLayout()

        # Admin checkbox
        admin_layout = QVBoxLayout()
        admin_label = QLabel("User Type:")
        admin_label.setStyleSheet("color: white; font-weight: bold;")
        self.is_admin_check = QCheckBox("Admin User")
        self.is_admin_check.setStyleSheet("color: white; margin-top: 10px;")
        admin_layout.addWidget(admin_label)
        admin_layout.addWidget(self.is_admin_check)

        # Book limit spinner
        limit_layout = QVBoxLayout()
        limit_label = QLabel("Book Limit:")
        limit_label.setStyleSheet("color: white; font-weight: bold;")
        self.book_limit_spin = QSpinBox()
        self.book_limit_spin.setRange(1, 10)
        self.book_limit_spin.setValue(3)
        self.book_limit_spin.setMinimumHeight(35)
        limit_layout.addWidget(limit_label)
        limit_layout.addWidget(self.book_limit_spin)

        settings_layout.addLayout(admin_layout)
        settings_layout.addLayout(limit_layout)

        # Add to form layout
        form_layout.addLayout(credentials_layout, 3)
        form_layout.addLayout(settings_layout, 2)

        # Buttons
        buttons_layout = QHBoxLayout()

        add_button = ActionButton("Add User", ActionButton.STYLE_SUCCESS)
        add_button.setIcon(QIcon("./assets/images/add_user_icon.png"))
        add_button.clicked.connect(self.add_user)

        delete_button = ActionButton("Delete Selected User", ActionButton.STYLE_DANGER)
        delete_button.setIcon(QIcon("./assets/images/delete_icon.png"))
        delete_button.clicked.connect(self.delete_user)

        buttons_layout.addWidget(add_button)
        buttons_layout.addWidget(delete_button)

        add_user_layout.addWidget(add_title)
        add_user_layout.addLayout(form_layout)
        add_user_layout.addLayout(buttons_layout)

        # Add components to main layout
        main_layout.addWidget(user_card, 3)
        main_layout.addWidget(add_user_card, 2)

        # Load users
        self.load_users()

    def load_users(self):
        try:
            users = UserDAO.get_all_users()

            self.user_table.setRowCount(len(users))
            for i, user in enumerate(users):
                self.user_table.setItem(i, 0, QTableWidgetItem(str(user.id)))

                # Username with bold for admin
                username_item = QTableWidgetItem(user.username)
                if user.is_admin:
                    username_item.setFont(QFont("Segoe UI", 9, QFont.Bold))
                self.user_table.setItem(i, 1, username_item)

                # Is Admin
                self.user_table.setItem(i, 2, QTableWidgetItem("Yes" if user.is_admin else "No"))

                # Book limit
                book_limit = str(user.book_limit) if user.book_limit is not None else "N/A"
                self.user_table.setItem(i, 3, QTableWidgetItem(book_limit))

                # Books issued
                self.user_table.setItem(i, 4, QTableWidgetItem(str(user.books_issued or 0)))

                # Action buttons for non-admin users
                if not user.is_admin:
                    action_widget = QWidget()
                    action_layout = QHBoxLayout(action_widget)
                    action_layout.setContentsMargins(5, 2, 5, 2)

                    edit_limit_btn = ActionButton("Edit Limit", ActionButton.STYLE_PRIMARY)
                    edit_limit_btn.clicked.connect(lambda checked, u_id=user.id: self.edit_book_limit(u_id))

                    action_layout.addWidget(edit_limit_btn)
                    self.user_table.setCellWidget(i, 5, action_widget)
                else:
                    # If admin, disable actions
                    self.user_table.setItem(i, 5, QTableWidgetItem("Admin"))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load users: {str(e)}")

    def add_user(self):
        username = self.new_username.text()
        password = self.new_password.text()
        is_admin = self.is_admin_check.isChecked()
        book_limit = self.book_limit_spin.value()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Username and password are required")
            return

        try:
            # Check if username already exists
            users = UserDAO.get_all_users()
            if any(u.username == username for u in users):
                QMessageBox.warning(self, "Error", "Username already exists")
                return

            user = User(
                username=username,
                password=password,
                is_admin=is_admin,
                book_limit=book_limit if not is_admin else None
            )

            if UserDAO.add_user(user):
                QMessageBox.information(self, "Success", "User added successfully!")

                # Clear form
                self.new_username.clear()
                self.new_password.clear()
                self.is_admin_check.setChecked(False)
                self.book_limit_spin.setValue(3)

                # Reload users
                self.load_users()
            else:
                QMessageBox.warning(self, "Error", "Failed to add user")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add user: {str(e)}")

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

        reply = QMessageBox.question(
            self, 'Delete User',
            f'Are you sure you want to delete user "{username}"?',
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                if UserDAO.delete_user(user_id):
                    QMessageBox.information(self, "Success", "User deleted successfully!")
                    self.load_users()
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete user")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete user: {str(e)}")

    def edit_book_limit(self, user_id):
        try:
            # Get current user info
            users = UserDAO.get_all_users()
            user = next((u for u in users if u.id == user_id), None)

            if not user:
                QMessageBox.warning(self, "Error", "User not found")
                return

            current_limit = user.book_limit or 3

            new_limit, ok = QInputDialog.getInt(
                self, "Edit Book Limit",
                f"Enter new book limit for {user.username}:",
                value=current_limit,
                min=1, max=20
            )

            if ok:
                if UserDAO.update_book_limit(user_id, new_limit):
                    QMessageBox.information(
                        self,
                        "Success",
                        f"Book limit for {user.username} updated to {new_limit}"
                    )
                    self.load_users()
                else:
                    QMessageBox.warning(self, "Error", "Failed to update book limit")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update book limit: {str(e)}")
