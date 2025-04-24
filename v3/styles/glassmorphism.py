from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QPalette, QColor, QFont, QFontDatabase, QIcon
from PyQt5.QtCore import Qt, QSize

class GlassmorphismStyle:
    PRIMARY_COLOR = "#6d28d9"  # Purple
    SECONDARY_COLOR = "#4f46e5"  # Indigo
    SUCCESS_COLOR = "#10b981"  # Green
    DANGER_COLOR = "#ef4444"  # Red
    WARNING_COLOR = "#f59e0b"  # Amber
    INFO_COLOR = "#3b82f6"  # Blue
    LIGHT_COLOR = "#f3f4f6"  # Light gray
    DARK_COLOR = "#1f2937"  # Dark gray

    GLASS_BG = "rgba(255, 255, 255, 0.25)"  # Transparent white
    GLASS_BORDER = "1px solid rgba(255, 255, 255, 0.3)"
    GLASS_SHADOW = "0 8px 32px 0 rgba(31, 38, 135, 0.37)"
    GLASS_BLUR = "backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);"

    @staticmethod
    def apply_base_styles(app):
        # Load custom fonts
        QFontDatabase.addApplicationFont("assets/fonts/Roboto-Regular.ttf")
        QFontDatabase.addApplicationFont("assets/fonts/Roboto-Bold.ttf")

        # Set application style
        app.setStyle("Fusion")

        # Set application-wide dark palette
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(31, 41, 55))  # Dark background
        palette.setColor(QPalette.WindowText, QColor(243, 244, 246))  # Light text
        palette.setColor(QPalette.Base, QColor(17, 24, 39))  # Darker background
        palette.setColor(QPalette.AlternateBase, QColor(31, 41, 55))
        palette.setColor(QPalette.ToolTipBase, QColor(243, 244, 246))
        palette.setColor(QPalette.ToolTipText, QColor(243, 244, 246))
        palette.setColor(QPalette.Text, QColor(243, 244, 246))
        palette.setColor(QPalette.Button, QColor(31, 41, 55))
        palette.setColor(QPalette.ButtonText, QColor(243, 244, 246))
        palette.setColor(QPalette.Link, QColor(79, 70, 229))  # Indigo
        palette.setColor(QPalette.Highlight, QColor(109, 40, 217))  # Purple
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))

        app.setPalette(palette)

        # Set default font
        font = QFont("Roboto", 10)
        app.setFont(font)

    @staticmethod
    def get_glass_stylesheet():
        """Basic glassmorphism style for widgets"""
        return f"""
            background-color: {GlassmorphismStyle.GLASS_BG};
            border: {GlassmorphismStyle.GLASS_BORDER};
            border-radius: 10px;
            /*{GlassmorphismStyle.GLASS_BLUR}*/
            box-shadow: {GlassmorphismStyle.GLASS_SHADOW};
        """

    @staticmethod
    def get_button_stylesheet(color, hover_color):
        """Styled button with glassmorphism effect"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {color};
            }}
            QPushButton:disabled {{
                background-color: #6b7280;
                color: #9ca3af;
            }}
        """

    @staticmethod
    def get_input_stylesheet():
        """Styled input fields with glassmorphism effect"""
        return f"""
            QLineEdit, QTextEdit, QComboBox, QSpinBox {{
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 5px;
                padding: 8px;
                color: white;
                selection-background-color: {GlassmorphismStyle.PRIMARY_COLOR};
            }}
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus {{
                border: 1px solid {GlassmorphismStyle.PRIMARY_COLOR};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            QComboBox::down-arrow {{
                image: url(assets/icons/dropdown-arrow.png);
                width: 16px;
                height: 16px;
            }}
            QComboBox QAbstractItemView {{
                background-color: #1f2937;
                border: 1px solid rgba(255, 255, 255, 0.2);
                selection-background-color: {GlassmorphismStyle.PRIMARY_COLOR};
                selection-color: white;
                outline: none;
            }}
        """

    @staticmethod
    def get_table_stylesheet():
        """Styled tables with glassmorphism effect"""
        return f"""
            QTableWidget {{
                background-color: rgba(17, 24, 39, 0.7);
                alternate-background-color: rgba(31, 41, 55, 0.7);
                border: {GlassmorphismStyle.GLASS_BORDER};
                border-radius: 10px;
                gridline-color: rgba(255, 255, 255, 0.1);
                outline: none;
            }}
            QTableWidget::item {{
                padding: 5px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            }}
            QTableWidget::item:selected {{
                background-color: rgba(109, 40, 217, 0.7);
                color: white;
            }}
            QHeaderView::section {{
                background-color: rgba(31, 41, 55, 0.9);
                padding: 5px;
                border: none;
                border-right: 1px solid rgba(255, 255, 255, 0.1);
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                font-weight: bold;
            }}
            QHeaderView::section:hover {{
                background-color: rgba(55, 65, 81, 0.9);
            }}
            QTableCornerButton::section {{
                background-color: rgba(31, 41, 55, 0.9);
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: rgba(17, 24, 39, 0.5);
                width: 12px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background-color: rgba(156, 163, 175, 0.5);
                min-height: 30px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: rgba(156, 163, 175, 0.8);
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                background-color: rgba(17, 24, 39, 0.5);
                height: 12px;
                margin: 0px;
            }}
            QScrollBar::handle:horizontal {{
                background-color: rgba(156, 163, 175, 0.5);
                min-width: 30px;
                border-radius: 6px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background-color: rgba(156, 163, 175, 0.8);
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
        """

    @staticmethod
    def get_tab_stylesheet():
        """Styled tab widget with glassmorphism effect"""
        return f"""
            QTabWidget::pane {{
                border: {GlassmorphismStyle.GLASS_BORDER};
                border-radius: 10px;
                background-color: rgba(17, 24, 39, 0.7);
                top: -1px;
            }}
            QTabBar::tab {{
                background-color: rgba(31, 41, 55, 0.7);
                color: white;
                padding: 10px 15px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }}
            QTabBar::tab:selected {{
                background-color: rgba(109, 40, 217, 0.7);
                font-weight: bold;
            }}
            QTabBar::tab:hover:!selected {{
                background-color: rgba(55, 65, 81, 0.7);
            }}
        """
        @staticmethod
        def apply_to_app(app):
            """Apply Glassmorphism styling to the entire application"""
            # Set application style to Fusion as base
            app.setStyle("Fusion")

            # Create dark palette
            palette = QPalette()

            # Set background gradient
            palette.setColor(QPalette.Window, QColor(31, 33, 42))
            palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
            palette.setColor(QPalette.Base, QColor(34, 36, 46, 160))
            palette.setColor(QPalette.AlternateBase, QColor(43, 45, 55, 160))
            palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
            palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
            palette.setColor(QPalette.Text, QColor(255, 255, 255))
            palette.setColor(QPalette.Button, QColor(43, 45, 55, 160))
            palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
            palette.setColor(QPalette.Link, QColor(121, 134, 203))
            palette.setColor(QPalette.Highlight, QColor(121, 134, 203))
            palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))

            app.setPalette(palette)

            # Load fonts
            try:
                QFontDatabase.addApplicationFont("./assets/fonts/Poppins-Regular.ttf")
                QFontDatabase.addApplicationFont("./assets/fonts/Poppins-Bold.ttf")
                app.setFont(QFont("Poppins", 10))
            except:
                # Fallback to system fonts if custom fonts not available
                app.setFont(QFont("Arial", 10))

            # Global application stylesheet
            app.setStyleSheet("""
                QMainWindow, QDialog {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                              stop:0 #1A1B25, stop:1 #2D2F3D);
                }

                QTabWidget::pane {
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 8px;
                    background-color: rgba(43, 45, 55, 0.5);
                    backdrop-filter: blur(10px);
                }

                QTabBar::tab {
                    background-color: rgba(43, 45, 55, 0.5);
                    color: #FFFFFF;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    min-width: 100px;
                    padding: 8px 12px;
                    margin-right: 2px;
                }

                QTabBar::tab:selected {
                    background-color: rgba(121, 134, 203, 0.7);
                }

                QPushButton {
                    background-color: rgba(121, 134, 203, 0.7);
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                }

                QPushButton:hover {
                    background-color: rgba(141, 154, 223, 0.8);
                }

                QPushButton:pressed {
                    background-color: rgba(101, 114, 183, 0.9);
                }

                QPushButton:disabled {
                    background-color: rgba(80, 80, 80, 0.5);
                    color: rgba(255, 255, 255, 0.4);
                }

                QLineEdit, QComboBox, QSpinBox {
                    background-color: rgba(43, 45, 55, 0.5);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 4px;
                    padding: 8px;
                    color: white;
                }

                QComboBox::drop-down {
                    border: none;
                }

                QTableWidget {
                    background-color: rgba(34, 36, 46, 0.5);
                    alternate-background-color: rgba(43, 45, 55, 0.5);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 8px;
                    gridline-color: rgba(255, 255, 255, 0.05);
                    color: white;
                }

                QTableWidget::item:selected {
                    background-color: rgba(121, 134, 203, 0.5);
                }

                QHeaderView::section {
                    background-color: rgba(43, 45, 55, 0.7);
                    color: white;
                    border: none;
                    padding: 8px;
                }

                QGroupBox {
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 8px;
                    background-color: rgba(43, 45, 55, 0.5);
                    margin-top: 16px;
                    font-weight: bold;
                }

                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top center;
                    padding: 0 8px;
                    color: white;
                }

                QScrollBar:vertical {
                    background-color: rgba(34, 36, 46, 0.5);
                    width: 12px;
                    border-radius: 6px;
                }

                QScrollBar::handle:vertical {
                    background-color: rgba(121, 134, 203, 0.7);
                    min-height: 20px;
                    border-radius: 6px;
                }

                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }

                QMessageBox {
                    background-color: rgba(43, 45, 55, 0.9);
                }

                QLabel {
                    color: white;
                }
            """)

    @staticmethod
    def apply_to_app(app):
        """Apply Glassmorphism styling to the entire application"""
        # Apply base styles first
        GlassmorphismStyle.apply_base_styles(app)
        
        # Global application stylesheet
        app.setStyleSheet("""
            QMainWindow, QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                        stop:0 #1A1B25, stop:1 #2D2F3D);
            }
            
            QTabWidget::pane {
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                background-color: rgba(43, 45, 55, 0.5);
                /*backdrop-filter: blur(10px);*/
            }
            
            QTabBar::tab {
                background-color: rgba(43, 45, 55, 0.5);
                color: #FFFFFF;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 100px;
                padding: 8px 12px;
                margin-right: 2px;
            }
            
            QTabBar::tab:selected {
                background-color: rgba(121, 134, 203, 0.7);
            }
            
            QPushButton {
                background-color: rgba(121, 134, 203, 0.7);
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            
            QPushButton:hover {
                background-color: rgba(141, 154, 223, 0.8);
            }
            
            QPushButton:pressed {
                background-color: rgba(101, 114, 183, 0.9);
            }
            
            QPushButton:disabled {
                background-color: rgba(80, 80, 80, 0.5);
                color: rgba(255, 255, 255, 0.4);
            }
            
            QLineEdit, QComboBox, QSpinBox {
                background-color: rgba(43, 45, 55, 0.5);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 4px;
                padding: 8px;
                color: white;
            }
            
            QComboBox::drop-down {
                border: none;
            }
            
            QTableWidget {
                background-color: rgba(34, 36, 46, 0.5);
                alternate-background-color: rgba(43, 45, 55, 0.5);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                gridline-color: rgba(255, 255, 255, 0.05);
                color: white;
            }
            
            QTableWidget::item:selected {
                background-color: rgba(121, 134, 203, 0.5);
            }
            
            QHeaderView::section {
                background-color: rgba(43, 45, 55, 0.7);
                color: white;
                border: none;
                padding: 8px;
            }
            
            QGroupBox {
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                background-color: rgba(43, 45, 55, 0.5);
                margin-top: 16px;
                font-weight: bold;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 8px;
                color: white;
            }
            
            QScrollBar:vertical {
                background-color: rgba(34, 36, 46, 0.5);
                width: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background-color: rgba(121, 134, 203, 0.7);
                min-height: 20px;
                border-radius: 6px;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            QMessageBox {
                background-color: rgba(43, 45, 55, 0.9);
            }
            
            QLabel {
                color: white;
            }
        """)