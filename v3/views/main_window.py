from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTabWidget, QLabel, QToolBar, QAction, QDialog)
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon
from components.action_button import ActionButton
from views.book_list_view import BookListWidget
from views.manage_books_view import ManageBooksWidget
from views.request_management_view import RequestManagementWidget
from views.admin_panel_view import AdminPanel
from views.login_view import LoginDialog
from views.dashboard_view import DashboardWidget

from utils.resources import get_icon, get_pixmap  # Add this import

class LibraryApp(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.is_admin = user.is_admin
        self.setWindowTitle("Library Management System")
        self.setGeometry(100, 100, 1200, 800)
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Create toolbar with glass effect
        toolbar = QToolBar()
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: rgba(43, 45, 55, 0.7);
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                padding: 5px;
            }
        """)
        self.addToolBar(toolbar)

        # Add user info and logout button to toolbar
        toolbar_widget = QWidget()
        toolbar_layout = QHBoxLayout(toolbar_widget)
        toolbar_layout.setContentsMargins(10, 5, 10, 5)

        # User info with icon
        user_widget = QWidget()
        user_layout = QHBoxLayout(user_widget)
        user_layout.setContentsMargins(0, 0, 0, 0)

        user_icon = QLabel()
        user_pixmap = get_pixmap("./assets/images/user_icon.png", "U", 24, 24)
        user_icon.setPixmap(user_pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        user_label = QLabel(f"Logged in as: {self.user.username}")
        user_label.setStyleSheet("color: white; font-weight: bold;")

        user_type = QLabel(f"({'Admin' if self.is_admin else 'User'})")
        user_type.setStyleSheet("color: rgba(255, 255, 255, 0.7);")

        user_layout.addWidget(user_icon)
        user_layout.addWidget(user_label)
        user_layout.addWidget(user_type)

        # Logout button
        logout_button = ActionButton("Logout", ActionButton.STYLE_DANGER)
        logout_icon = get_icon("./assets/images/logout_icon.png", "X")
        logout_button.setIcon(logout_icon)
        logout_button.clicked.connect(self.logout)

        toolbar_layout.addWidget(user_widget)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(logout_button)

        toolbar.addWidget(toolbar_widget)

        # Create main content area with tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                padding: 10px;
            }
        """)
        # Create dashboard and connect signals
        dashboard = DashboardWidget(self.user, self)
        dashboard.showBooksSignal.connect(lambda: self.tabs.setCurrentIndex(1))
        dashboard.showManageBooksSignal.connect(lambda: self.tabs.setCurrentIndex(2))
        dashboard.showRequestsSignal.connect(lambda: self.tabs.setCurrentIndex(3))
        dashboard.showAdminPanelSignal.connect(lambda: self.tabs.setCurrentIndex(4))
        
        # Add dashboard as the first tab
        self.tabs.addTab(dashboard, "Dashboard")
        
        # Add other tabs
        self.book_list_widget = BookListWidget(self.user)
        self.tabs.addTab(self.book_list_widget, "Book Inventory")

        if self.is_admin:
            self.manage_books_widget = ManageBooksWidget()
            self.tabs.addTab(self.manage_books_widget, "Manage Books")
            
            self.request_management_widget = RequestManagementWidget()
            self.tabs.addTab(self.request_management_widget, "Manage Requests")
            
            self.admin_panel = AdminPanel()
            self.tabs.addTab(self.admin_panel, "Admin Panel")

        main_layout.addWidget(self.tabs)

    def logout(self):
        from PyQt5.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, 'Logout',
            'Are you sure you want to logout?',
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Create and show a new login dialog
            login_dialog = LoginDialog()

            # When login is successful, update this window with new user data
            def on_login_successful(user):
                global main_window
                self.close()
                main_window = LibraryApp(user)
                main_window.show()

            login_dialog.loginSuccessful.connect(on_login_successful)

            # Hide this window (don't close it yet)
            self.hide()

            # If login is cancelled, close this window
            if login_dialog.exec_() != QDialog.Accepted:
                self.close()

    def show_login(self):
        login = LoginDialog()
        login.loginSuccessful.connect(self.on_login_successful)

        if login.exec_() != QDialog.Accepted:
            self.close()

    @pyqtSlot(object)
    def on_login_successful(self, user):
        self.close()
        new_window = LibraryApp(user)
        new_window.show()
