from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
                            QTableWidgetItem, QHeaderView, QComboBox, QMessageBox,
                            QPushButton, QGroupBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont, QColor
from components.glass_card import GlassCard
from components.action_button import ActionButton
from database.request_dao import BookRequestDAO
from database.book_dao import BookDAO
from database.user_dao import UserDAO
from database.connection import DatabaseConnection

class RequestManagementWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header section with stats
        header_card = GlassCard()
        header_layout = QVBoxLayout(header_card)

        title = QLabel("Request Management")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")

        # Filter options
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(15)

        filter_label = QLabel("View:")
        filter_label.setStyleSheet("color: white; font-size: 14px;")

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Pending Requests", "Request History"])
        self.filter_combo.setMinimumHeight(35)
        self.filter_combo.currentTextChanged.connect(self.load_requests)

        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_combo)
        filter_layout.addStretch()

        # Statistics section
        stats_box = QGroupBox("Request Statistics")
        stats_box.setStyleSheet("""
            QGroupBox {
                background-color: rgba(43, 45, 55, 0.5);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                margin-top: 15px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: white;
            }
        """)

        stats_layout = QHBoxLayout(stats_box)
        stats_layout.setSpacing(20)

        # Create stat cards
        self.pending_count = self.create_stat_card("Pending", "0", "#f59e0b")  # Amber
        self.approved_count = self.create_stat_card("Approved", "0", "#10b981")  # Green
        self.rejected_count = self.create_stat_card("Rejected", "0", "#ef4444")  # Red

        stats_layout.addWidget(self.pending_count)
        stats_layout.addWidget(self.approved_count)
        stats_layout.addWidget(self.rejected_count)

        # Add header components
        header_layout.addWidget(title)
        header_layout.addLayout(filter_layout)
        header_layout.addWidget(stats_box)

        # Requests table
        table_card = GlassCard()
        table_layout = QVBoxLayout(table_card)

        self.requests_table = QTableWidget()
        self.requests_table.setColumnCount(9)
        self.requests_table.setHorizontalHeaderLabels([
            "Request ID", "Book Title", "Book ID", "Student Name",
            "Request Date", "Status", "Books Issued", "Available Limit", "Actions"
        ])

        # Set table properties
        self.requests_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.requests_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.requests_table.setAlternatingRowColors(True)
        self.requests_table.verticalHeader().setVisible(False)

        table_layout.addWidget(self.requests_table)

        # Add components to main layout
        layout.addWidget(header_card, 2)
        layout.addWidget(table_card, 5)

        # Load initial data
        self.load_requests()
        self.update_statistics()

    def create_stat_card(self, title, value, color):
        """Create a statistic card with glassy effect"""
        card = QWidget()
        card.setStyleSheet(f"""
            background-color: rgba(43, 45, 55, 0.7);
            border: 1px solid {color};
            border-radius: 8px;
            padding: 10px;
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(5)

        value_label = QLabel(value)
        value_label.setStyleSheet(f"color: {color}; font-size: 32px; font-weight: bold;")
        value_label.setAlignment(Qt.AlignCenter)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: white; font-size: 14px;")
        title_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(value_label)
        layout.addWidget(title_label)

        return card

    def load_requests(self):
        try:
            view_type = self.filter_combo.currentText()

            # Get requests
            if view_type == "Pending Requests":
                requests = BookRequestDAO.get_pending_requests()
            else:  # Request History
                requests = BookRequestDAO.get_request_history()

            self.requests_table.setRowCount(len(requests))
            for i, req in enumerate(requests):
                # Request ID
                self.requests_table.setItem(i, 0, QTableWidgetItem(str(req[0])))

                # Book Title
                title_item = QTableWidgetItem(req[1])
                title_item.setFont(QFont("Segoe UI", 9, QFont.Bold))
                self.requests_table.setItem(i, 1, title_item)

                # Book ID
                self.requests_table.setItem(i, 2, QTableWidgetItem(req[2]))

                # Student Name
                self.requests_table.setItem(i, 3, QTableWidgetItem(req[3]))

                # Request Date
                request_date = req[5].strftime('%Y-%m-%d %H:%M') if req[5] else ""
                self.requests_table.setItem(i, 4, QTableWidgetItem(request_date))

                # Status with color-coding
                status_item = QTableWidgetItem(req[6])
                if req[6] == "Pending":
                    status_item.setForeground(QColor("#f59e0b"))  # Amber
                elif req[6] == "Approved":
                    status_item.setForeground(QColor("#10b981"))  # Green
                elif req[6] == "Rejected":
                    status_item.setForeground(QColor("#ef4444"))  # Red
                elif req[6] == "Returned":
                    status_item.setForeground(QColor("#3b82f6"))  # Blue
                self.requests_table.setItem(i, 5, status_item)

                # Books Issued
                self.requests_table.setItem(i, 6, QTableWidgetItem(str(req[7])))

                # Available Limit
                remaining = req[8] - req[7]
                limit_item = QTableWidgetItem(f"{remaining}/{req[8]}")
                if remaining <= 0:
                    limit_item.setForeground(QColor("#ef4444"))  # Red
                self.requests_table.setItem(i, 7, limit_item)

                # Action buttons or completion info
                if req[6] == "Pending":
                    # Add action buttons - code remains the same
                    action_widget = QWidget()
                    action_layout = QHBoxLayout(action_widget)
                    action_layout.setContentsMargins(5, 2, 5, 2)
                    action_layout.setSpacing(5)

                    if remaining > 0:  # If user hasn't reached their limit
                        approve_btn = ActionButton("Approve", ActionButton.STYLE_SUCCESS)
                        approve_btn.clicked.connect(
                            lambda checked, rid=req[0], bid=req[2], uid=req[4]:
                            self.handle_request(rid, bid, uid, "Approved")
                        )
                        action_layout.addWidget(approve_btn)

                    reject_btn = ActionButton("Reject", ActionButton.STYLE_DANGER)
                    reject_btn.clicked.connect(
                        lambda checked, rid=req[0], bid=req[2], uid=req[4]:
                        self.handle_request(rid, bid, uid, "Rejected")
                    )

                    action_layout.addWidget(reject_btn)
                    self.requests_table.setCellWidget(i, 8, action_widget)
                else:
                    # For history items, show approval date
                    approval_date = ""
                    if len(req) > 9 and req[9]:  # Approval date
                        approval_date = req[9].strftime('%Y-%m-%d %H:%M')
                    self.requests_table.setItem(i, 8, QTableWidgetItem(approval_date))

            self.update_statistics()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load requests: {str(e)}")
    def update_statistics(self):
        try:
            stats = BookRequestDAO.get_request_statistics()

            # Update stat cards
            self.pending_count.findChild(QLabel).setText(str(stats.get('Pending', 0)))
            self.approved_count.findChild(QLabel).setText(str(stats.get('Approved', 0)))
            self.rejected_count.findChild(QLabel).setText(str(stats.get('Rejected', 0)))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update statistics: {str(e)}")

    def handle_request(self, request_id, book_id, user_id, status):
        try:
            print(f"Request handling - ID: {request_id}, Book: {book_id}, User: {user_id}, Status: {status}")
            
            if status == "Approved":
                # Get current user info
                users = UserDAO.get_all_users()
                user = next((u for u in users if u.id == user_id), None)
                
                print(f"User found: {user.username if user else 'None'}, Books issued: {user.books_issued if user else 'N/A'}")

                if user and user.books_issued >= user.book_limit:
                    QMessageBox.warning(
                        self,
                        "Limit Exceeded",
                        f"User has reached their book limit ({user.book_limit} books)"
                    )
                    return

                # Get book info and check availability
                book = BookDAO.get_book_by_id(book_id)
                print(f"Book found: {book.title if book else 'None'}, Status: {book.status if book else 'N/A'}")
                
                if not book:
                    QMessageBox.warning(self, "Error", "Book not found")
                    return

                if book.status != "Available":
                    QMessageBox.warning(self, "Error", "Book is no longer available")
                    return

                # Create a connection for transaction
                conn = DatabaseConnection.get_instance().get_connection()
                try:
                    with conn.cursor() as cursor:
                        # Update book status to 'Issued' and set issuer_id
                        print(f"Updating book status to 'Issued', setting issuer_id to {user_id}")
                        cursor.execute("""
                            UPDATE books 
                            SET status = 'Issued', 
                                issuer_id = %s, 
                                issue_date = NOW(), 
                                return_date = DATE_ADD(NOW(), INTERVAL 14 DAY) 
                            WHERE book_id = %s
                        """, (user_id, book_id))
                        book_rows = cursor.rowcount
                        print(f"Book update rows affected: {book_rows}")
                        
                        # Increment user's books_issued count
                        print(f"Incrementing books_issued for user {user_id}")
                        cursor.execute("""
                            UPDATE users 
                            SET books_issued = books_issued + 1 
                            WHERE id = %s
                        """, (user_id,))
                        user_rows = cursor.rowcount
                        print(f"User update rows affected: {user_rows}")
                        
                        # Update request status
                        print(f"Updating request status to {status}")
                        cursor.execute("""
                            UPDATE book_requests 
                            SET status = %s, 
                                approval_date = NOW() 
                            WHERE id = %s
                        """, (status, request_id))
                        request_rows = cursor.rowcount
                        print(f"Request update rows affected: {request_rows}")
                        
                        conn.commit()
                        print("Transaction committed successfully")
                except Exception as e:
                    conn.rollback()
                    print(f"Database error during approval: {e}")
                    raise
                finally:
                    conn.close()
            else:
                # Just update request status for rejections
                print(f"Updating request to rejected status")
                BookRequestDAO.update_request_status(request_id, status)

            QMessageBox.information(
                self,
                "Success",
                f"Request {status.lower()} successfully!"
            )
            self.load_requests()

        except Exception as e:
            print(f"Error in handle_request: {e}")
            QMessageBox.critical(self, "Error", f"Failed to process request: {str(e)}")
