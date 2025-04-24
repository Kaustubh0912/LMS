import sys
import os
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtGui import QIcon
from styles.glassmorphism import GlassmorphismStyle
from views.login_view import LoginDialog
from views.main_window import LibraryApp

def main():
    # Create application directory structure if it doesn't exist
    os.makedirs('./assets/images', exist_ok=True)
    os.makedirs('./assets/fonts', exist_ok=True)
    os.makedirs('./utils', exist_ok=True)

    # Initialize the application
    app = QApplication(sys.argv)
    app.setApplicationName("Library Management System")
    
    # Set window icon with fallback
    from utils.resources import get_icon
    app.setWindowIcon(get_icon("./assets/images/app_icon.png", "LMS"))

    # Apply Glassmorphism style
    GlassmorphismStyle.apply_to_app(app)

    # Store the main window as a global variable to prevent garbage collection
    global main_window
    main_window = None
    
    def show_main_window(user):
        global main_window
        print(f"Creating main window for user: {user.username}")
        main_window = LibraryApp(user)
        main_window.show()
    
    # Show login dialog
    login_dialog = LoginDialog()
    login_dialog.loginSuccessful.connect(show_main_window)
    
    # Show the login dialog
    if login_dialog.exec_() != QDialog.Accepted:
        return 0  # Exit if login is canceled
    
    # Start the application event loop only if login was successful
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())