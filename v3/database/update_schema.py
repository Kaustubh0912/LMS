from database.connection import DatabaseConnection

def update_database_schema():
    """Update the database schema with new tables and columns for dashboard functionality"""
    conn = DatabaseConnection.get_instance().get_connection()
    try:
        with conn.cursor() as cursor:
            # Add genre column to books table if it doesn't exist
            cursor.execute("""
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = 'books' AND COLUMN_NAME = 'genre'
            """)
            if cursor.fetchone()[0] == 0:
                cursor.execute("ALTER TABLE books ADD COLUMN genre VARCHAR(50)")

            # Create notifications table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    message TEXT NOT NULL,
                    created_at DATETIME NOT NULL,
                    is_read BOOLEAN DEFAULT FALSE,
                    notification_type VARCHAR(20),
                    related_id INT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # Create reviews table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reviews (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    book_id VARCHAR(50) NOT NULL,
                    user_id INT NOT NULL,
                    rating INT NOT NULL,
                    review_text TEXT,
                    review_date DATETIME NOT NULL,
                    FOREIGN KEY (book_id) REFERENCES books(book_id),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # Create reservations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reservations (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    book_id VARCHAR(50) NOT NULL,
                    user_id INT NOT NULL,
                    reservation_date DATETIME NOT NULL,
                    status VARCHAR(20) DEFAULT 'Active',
                    notification_sent BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (book_id) REFERENCES books(book_id),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # Create activity logs table for dashboard analytics
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activity_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    action_type VARCHAR(50) NOT NULL,
                    entity_type VARCHAR(20) NOT NULL,
                    entity_id VARCHAR(50),
                    details TEXT,
                    timestamp DATETIME NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            conn.commit()

    finally:
        conn.close()
