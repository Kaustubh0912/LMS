from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon
from components.glass_card import GlassCard
from components.action_button import ActionButton
from database.user_dao import UserDAO
from utils.resources import get_pixmap  # Add this import

class LoginDialog(QDialog):
    loginSuccessful = pyqtSignal(object)  # Signal to emit user object

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Library Management System - Login")
        self.setMinimumWidth(400)
        self.setMinimumHeight(450)
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Logo section
        logo_label = QLabel()
        logo_pixmap = get_pixmap("./assets/images/library_logo.png", "LMS", 80, 80)
        logo_label.setPixmap(logo_pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignCenter)

        title_label = QLabel("Library Management System")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        title_label.setAlignment(Qt.AlignCenter)

        # Glass card for login form
        login_card = GlassCard()
        card_layout = QVBoxLayout(login_card)
        card_layout.setSpacing(20)

        form_title = QLabel("Login to your account")
        form_title.setStyleSheet("font-size: 16px; color: white; font-weight: bold;")
        form_title.setAlignment(Qt.AlignCenter)

        # Username field
        username_layout = QVBoxLayout()
        username_label = QLabel("Username")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)

        # Password field
        password_layout = QVBoxLayout()
        password_label = QLabel("Password")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter your password")
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)

        # Login button
        login_button = ActionButton("Login", ActionButton.STYLE_PRIMARY)
        login_button.setMinimumHeight(40)
        login_button.clicked.connect(self.handle_login)

        # Exit button
        exit_button = ActionButton("Exit", ActionButton.STYLE_DANGER)
        exit_button.setMinimumHeight(40)
        exit_button.clicked.connect(self.reject)

        # Add all elements to card layout
        card_layout.addWidget(form_title)
        card_layout.addLayout(username_layout)
        card_layout.addLayout(password_layout)
        card_layout.addWidget(login_button)
        card_layout.addWidget(exit_button)

        # Add all elements to main layout
        main_layout.addWidget(logo_label)
        main_layout.addWidget(title_label)
        main_layout.addWidget(login_card)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Login Failed", "Please enter both username and password")
            return

        user = UserDAO.get_by_credentials(username, password)

        if user:
            self.user_data = user  # Store the user data
            self.loginSuccessful.emit(user)
            self.accept()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password")
