from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QGridLayout, QPushButton)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap
from components.glass_card import GlassCard
from components.action_button import ActionButton
from database.book_dao import BookDAO
from database.user_dao import UserDAO
from database.request_dao import BookRequestDAO
from utils.resources import get_pixmap, get_icon
from database.connection import DatabaseConnection
import traceback

class DashboardWidget(QWidget):
    # Add signals to navigate to specific tabs
    showBooksSignal = pyqtSignal()
    showManageBooksSignal = pyqtSignal()
    showRequestsSignal = pyqtSignal()
    showAdminPanelSignal = pyqtSignal()
    
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.user = user
        self.parent = parent
        self.setup_ui()
        
    def setup_ui(self):
        try:
            layout = QVBoxLayout(self)
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(20)
            
            # Welcome section
            welcome_card = GlassCard()
            welcome_layout = QHBoxLayout(welcome_card)
            
            # User avatar
            avatar_label = QLabel()
            avatar_pixmap = get_pixmap("./assets/images/user_avatar.png", 
                                    self.user.username[0].upper(), 80, 80)
            avatar_label.setPixmap(avatar_pixmap)
            avatar_label.setFixedSize(80, 80)
            
            # Welcome text
            welcome_text = QVBoxLayout()
            title = QLabel(f"Welcome, {self.user.username}!")
            title.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
            
            subtitle = QLabel("Here's an overview of your library activity")
            subtitle.setStyleSheet("font-size: 14px; color: rgba(255,255,255,0.7);")
            
            welcome_text.addWidget(title)
            welcome_text.addWidget(subtitle)
            
            welcome_layout.addWidget(avatar_label)
            welcome_layout.addLayout(welcome_text)
            welcome_layout.addStretch()
            
            # Statistics cards in grid
            stats_grid = QGridLayout()
            stats_grid.setSpacing(15)
            
            if self.user.is_admin:
                # Admin statistics
                total_books = self.create_stat_card("Total Books", 
                                                self.get_total_books(), 
                                                "books")
                
                total_users = self.create_stat_card("Registered Users", 
                                                self.get_total_users(), 
                                                "users")
                
                pending_requests = self.create_stat_card("Pending Requests", 
                                                    self.get_pending_requests(), 
                                                    "pending")
                
                books_issued = self.create_stat_card("Books Issued", 
                                                self.get_issued_books(), 
                                                "issued")
                
                stats_grid.addWidget(total_books, 0, 0)
                stats_grid.addWidget(total_users, 0, 1)
                stats_grid.addWidget(pending_requests, 1, 0)
                stats_grid.addWidget(books_issued, 1, 1)
            else:
                # Regular user statistics
                books_borrowed = self.create_stat_card("Books Borrowed", 
                                                self.user.books_issued if hasattr(self.user, 'books_issued') else 0, 
                                                "borrowed")
                
                # Calculate available quota safely
                book_limit = getattr(self.user, 'book_limit', 3)
                books_issued = getattr(self.user, 'books_issued', 0)
                available_quota = book_limit - books_issued
                
                available_quota_card = self.create_stat_card("Available Quota", 
                                                    available_quota, 
                                                    "quota")
                
                pending_requests = self.create_stat_card("Your Pending Requests", 
                                                    self.get_user_pending_requests(), 
                                                    "pending")
                
                stats_grid.addWidget(books_borrowed, 0, 0)
                stats_grid.addWidget(available_quota_card, 0, 1)
                stats_grid.addWidget(pending_requests, 1, 0, 1, 2)
            
            # Quick actions section
            actions_card = GlassCard()
            actions_layout = QVBoxLayout(actions_card)
            
            actions_title = QLabel("Quick Actions")
            actions_title.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
            
            # Create and add action buttons
            actions_grid = QGridLayout()
            actions_grid.setSpacing(10)
            
            if self.user.is_admin:
                add_book_btn = self.create_action_button("Add New Book", 
                                                    "plus", 
                                                    "#10b981")  # Green
                add_book_btn.clicked.connect(self.navigate_to_manage_books)
                
                manage_users_btn = self.create_action_button("Manage Users", 
                                                        "users", 
                                                        "#3b82f6")  # Blue
                manage_users_btn.clicked.connect(self.navigate_to_admin_panel)
                
                approve_requests_btn = self.create_action_button("Pending Requests", 
                                                            "clock", 
                                                            "#f59e0b")  # Amber
                approve_requests_btn.clicked.connect(self.navigate_to_requests)
                
                reports_btn = self.create_action_button("Book Inventory", 
                                                    "books", 
                                                    "#8b5cf6")  # Purple
                reports_btn.clicked.connect(self.navigate_to_books)
                
                actions_grid.addWidget(add_book_btn, 0, 0)
                actions_grid.addWidget(manage_users_btn, 0, 1)
                actions_grid.addWidget(approve_requests_btn, 1, 0)
                actions_grid.addWidget(reports_btn, 1, 1)
            else:
                # Update the regular user actions section
                browse_books_btn = self.create_action_button("Browse Books", 
                                                        "search", 
                                                        "#3b82f6")  # Blue
                browse_books_btn.clicked.connect(self.navigate_to_books)
                
                request_book_btn = self.create_action_button("Request Book", 
                                                        "book", 
                                                        "#10b981")  # Green
                request_book_btn.clicked.connect(self.navigate_to_books)
                
                view_requests_btn = self.create_action_button("My Requests", 
                                                        "list", 
                                                        "#f59e0b")  # Amber
                view_requests_btn.clicked.connect(self.show_my_requests)
                
                actions_grid.addWidget(browse_books_btn, 0, 0)
                actions_grid.addWidget(request_book_btn, 0, 1)
                actions_grid.addWidget(view_requests_btn, 1, 0, 1, 2)
            
            actions_layout.addWidget(actions_title)
            actions_layout.addLayout(actions_grid)
            
            # Add all components to main layout
            layout.addWidget(welcome_card)
            layout.addLayout(stats_grid)
            layout.addWidget(actions_card)
            
        except Exception as e:
            print(f"Error in dashboard setup_ui: {str(e)}")
            traceback.print_exc()
        
    def create_stat_card(self, title, value, icon_name):
        try:
            card = GlassCard()
            layout = QHBoxLayout(card)
            
            # Icon
            icon_label = QLabel()
            icon_pixmap = get_pixmap(f"./assets/images/{icon_name}_icon.png", 
                                  icon_name[0].upper(), 40, 40)
            icon_label.setPixmap(icon_pixmap)
            icon_label.setFixedSize(40, 40)
            
            # Text content
            text_layout = QVBoxLayout()
            value_label = QLabel(str(value))
            value_label.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
            
            title_label = QLabel(title)
            title_label.setStyleSheet("font-size: 14px; color: rgba(255,255,255,0.7);")
            
            text_layout.addWidget(value_label)
            text_layout.addWidget(title_label)
            
            layout.addWidget(icon_label)
            layout.addLayout(text_layout)
            layout.addStretch()
            
            return card
        except Exception as e:
            print(f"Error creating stat card: {str(e)}")
            # Return an empty widget if there's an error
            empty_card = GlassCard()
            empty_layout = QVBoxLayout(empty_card)
            empty_layout.addWidget(QLabel("Error loading card"))
            return empty_card
    
    def create_action_button(self, text, icon_name, color):
        try:
            # Fix color format if needed - ensure it's a valid hex color
            if color and not color.startswith("#"):
                color = "#" + color
            
            button = ActionButton(text)
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color}80;  /* 50% opacity */
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 15px;
                    text-align: left;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {color};
                }}
            """)
            
            # Set icon from resource utility
            icon = get_icon(f"./assets/images/{icon_name}_icon.png", icon_name[0].upper())
            button.setIcon(icon)
            button.setIconSize(QSize(24, 24))
            
            return button
        except Exception as e:
            print(f"Error creating action button: {str(e)}")
            # Return a basic button if there's an error
            return QPushButton(text)
    
    # Navigation methods
    def navigate_to_books(self):
        # Find the parent QTabWidget and switch to Books tab
        self.showBooksSignal.emit()
        if self.parent and hasattr(self.parent, 'tabs'):
            self.parent.tabs.setCurrentIndex(1)  # Books tab index
    
    def navigate_to_manage_books(self):
        # Navigate to Manage Books tab (admin only)
        self.showManageBooksSignal.emit()
        if self.parent and hasattr(self.parent, 'tabs'):
            self.parent.tabs.setCurrentIndex(2)  # Manage Books tab index
    
    def navigate_to_requests(self):
        # Navigate to Requests Management tab (admin only)
        self.showRequestsSignal.emit()
        if self.parent and hasattr(self.parent, 'tabs'):
            self.parent.tabs.setCurrentIndex(3)  # Requests tab index
    
    def navigate_to_admin_panel(self):
        # Navigate to Admin Panel tab (admin only)
        self.showAdminPanelSignal.emit()
        if self.parent and hasattr(self.parent, 'tabs'):
            self.parent.tabs.setCurrentIndex(4)  # Admin Panel tab index
    
    def show_my_requests(self):
        # For regular users - navigate to Books tab and filter to "My Requests"
        self.navigate_to_books()
        # Find the filter combo box in the Books tab and set it to "My Requests"
        if self.parent and hasattr(self.parent, 'tabs'):
            books_tab = self.parent.tabs.widget(1)
            if hasattr(books_tab, 'filter_combo'):
                books_tab.filter_combo.setCurrentText("My Requests")
    
    # Data retrieval methods
    def get_total_books(self):
        try:
            conn = DatabaseConnection.get_instance().get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM books")
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            print(f"Error getting total books: {str(e)}")
            return 0
        finally:
            if 'conn' in locals():
                conn.close()
            
    def get_total_users(self):
        try:
            conn = DatabaseConnection.get_instance().get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = 0")
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            print(f"Error getting total users: {str(e)}")
            return 0
        finally:
            if 'conn' in locals():
                conn.close()
            
    def get_pending_requests(self):
        try:
            conn = DatabaseConnection.get_instance().get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM book_requests WHERE status = 'Pending'")
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            print(f"Error getting pending requests: {str(e)}")
            return 0
        finally:
            if 'conn' in locals():
                conn.close()
            
    def get_issued_books(self):
        try:
            conn = DatabaseConnection.get_instance().get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM books WHERE status = 'Issued'")
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            print(f"Error getting issued books: {str(e)}")
            return 0
        finally:
            if 'conn' in locals():
                conn.close()
            
    def get_user_pending_requests(self):
        try:
            conn = DatabaseConnection.get_instance().get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM book_requests WHERE user_id = %s AND status = 'Pending'", 
                             (self.user.id,))
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            print(f"Error getting user pending requests: {str(e)}")
            return 0
        finally:
            if 'conn' in locals():
                conn.close()