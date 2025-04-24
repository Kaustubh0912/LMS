# Library Management System (LMS)

A modern **Library Management System** built using **PyQt5** and **MySQL** with a beautiful Glassmorphism UI. This application allows users to manage books, handle book requests, and perform administrative tasks such as user management and request approvals.

---

## Features

- **User Authentication**:
  - Login as an **Admin** or **Student**.
  - Admins have full access to manage books, users, and requests.
  - Students can view available books, request books, and check their request status.

- **Dashboard**:
  - Interactive dashboard with statistics and quick access buttons.
  - Personalized view for administrators and students.
  - Real-time statistics on books, users, and pending requests.

- **Book Management**:
  - Add, edit, and delete books.
  - Advanced search and filtering capabilities.
  - Track book status (Available, Issued).
  - Manage book requests and approvals.

- **User Management**:
  - Admins can add, edit, and delete users.
  - Set book limits for students.
  - Monitor user activity and borrowed books.

- **Request Management**:
  - Students can request books.
  - Admins can approve or reject requests.
  - Track pending, approved, and rejected requests with visual indicators.

- **Search and Filter**:
  - Enhanced search functionality across multiple fields.
  - Filter books by availability or request status.
  - Save and manage search preferences.

- **Modern Glassmorphism UI**:
  - Beautiful transparent glass-like interface.
  - Responsive design with smooth animations.
  - Dark theme for enhanced visibility and reduced eye strain.

---

## Prerequisites

Before running the application, ensure you have the following installed:

1. **Python 3.7+** - [Download Python](https://www.python.org/downloads/)
2. **MySQL Server** - [Download MySQL](https://dev.mysql.com/downloads/mysql/)
3. Required Python packages:
   ```bash
   pip install PyQt5 pymysql python-dotenv cryptography
   ```

---

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/LMS.git
   cd LMS
   ```

2. **Set Up Environment Variables**:
   - Create a `.env` file in the project root with the following content:
     ```
     DB_HOST=localhost
     DB_USER=your_mysql_username
     DB_PASSWORD=your_mysql_password
     DB_NAME=library_db
     DB_CHARSET=utf8mb4
     ```

3. **Create Asset Directories**:
   ```bash
   mkdir -p assets/images
   mkdir -p assets/fonts
   ```

4. **Run the Application**:
   ```bash
   python v3/main.py
   ```

---

## Architecture

The application follows a modular architecture for improved maintainability and extensibility:

```
lms/
├── assets/             # Images, icons, and fonts
├── components/         # Reusable UI components
├── database/           # Database connections and DAOs
├── models/             # Data models
├── styles/             # UI styling
├── utils/              # Utility functions
├── views/              # Application screens
└── main.py             # Application entry point
```

---

## Usage

### **Login**
- Use the following credentials to log in:
  - **Admin**:
    - Username: `admin`
    - Password: `admin123`
  - **Student**:
    - Register a new student account via the Admin Panel.

### **Dashboard**
- View statistics and quick access to key features.
- Admin dashboard shows total books, users, and pending requests.
- Student dashboard shows borrowed books, available quota, and pending requests.

### **Admin Features**
- **Manage Books**:
  - Add, edit, or delete books with an enhanced interface.
  - Search books using the new search feature.
  - Return borrowed books with a single click.
- **Manage Users**:
  - Add, edit, or delete users.
  - Set book limits for students.
- **Request Management**:
  - View statistics on pending, approved, and rejected requests.
  - Approve or reject book requests with enhanced visibility.

### **Student Features**
- **Browse Books**:
  - Use advanced search and filter features.
  - View book availability and details.
- **Request Books**:
  - Request available books with a streamlined process.
  - Track request status with visual indicators.

---
<!-- 
## Screenshots

### Login Page with Glassmorphism UI
![Login Page](screenshots/login_glassmorphism.png)

### Admin Dashboard
![Admin Dashboard](screenshots/admin_dashboard.png)

### Book Management
![Book Management](screenshots/book_management.png)

### Request Management
![Request Management](screenshots/request_management_glass.png)

### User Management
![User Management](screenshots/user_management.png)

--- -->

## Database Schema

The application uses the following tables:

1. **books**:
   - `id` (Primary Key)
   - `title` (Book Title)
   - `book_id` (Unique Book ID)
   - `author` (Author Name)
   - `status` (Available, Issued)
   - `issuer_id` (User ID of the Issuer)
   - `course_code` (Course Code)
   - `issue_date` (Date of Issue)
   - `return_date` (Date of Return)
   - `genre` (Book Genre)

2. **users**:
   - `id` (Primary Key)
   - `username` (Unique Username)
   - `password` (Password)
   - `is_admin` (Boolean: True for Admin, False for Student)
   - `book_limit` (Maximum Books a Student Can Issue)
   - `books_issued` (Number of Books Currently Issued)

3. **book_requests**:
   - `id` (Primary Key)
   - `book_id` (Foreign Key to `books`)
   - `user_id` (Foreign Key to `users`)
   - `status` (Pending, Approved, Rejected, Returned)
   - `request_date` (Date of Request)
   - `approval_date` (Date of Approval/Rejection)
   - `notes` (Additional Notes)

4. **notifications**:
   - `id` (Primary Key)
   - `user_id` (Foreign Key to `users`)
   - `message` (Notification Text)
   - `created_at` (Creation Timestamp)
   - `is_read` (Boolean: Whether notification has been read)
   - `notification_type` (Type of notification)
   - `related_id` (Related entity ID)

---

## New Features in v3

1. **Glassmorphism UI**:
   - Beautiful transparent glass-like interface elements
   - Smooth hover effects and transitions
   - Improved visual hierarchy and readability

2. **Interactive Dashboard**:
   - User-specific statistics and quick actions
   - Real-time data display
   - Navigation shortcuts to common tasks

3. **Enhanced Book Management**:
   - Advanced search functionality in the admin panel
   - Improved book detail display
   - More intuitive book return process

4. **Improved Navigation**:
   - Tab-based navigation with better visual indicators
   - Quick access buttons in the dashboard
   - More intuitive user flow

5. **Better Error Handling**:
   - Graceful handling of missing resources
   - Improved database connection management
   - Descriptive error messages

---

## Future Enhancements

- **Book Recommendations**: Personalized book recommendations based on borrowing history
- **Fine Management**: Track and manage overdue book fines
- **Email Notifications**: Send email alerts for due dates and request updates
- **Barcode Integration**: Support for scanning book barcodes
- **Reports and Analytics**: Advanced reporting and data visualization
- **User Profiles**: Enhanced user profiles with reading preferences

---

## Contributing

Contributions are welcome! If you'd like to contribute, please follow these steps:

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---



Enjoy using the Library Management System! If you have any questions or issues, feel free to open an issue on GitHub.

---
Made with ❤️ by [NOX]
