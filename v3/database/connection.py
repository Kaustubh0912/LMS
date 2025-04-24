import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

class DatabaseConnection:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if DatabaseConnection._instance is not None:
            raise Exception("This class is a singleton!")

        self.host = os.getenv("DB_HOST")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.db_name = os.getenv("DB_NAME")
        self.charset = os.getenv("DB_CHARSET", "utf8mb4")
        self.initialize_database()

    def get_connection(self):
        return pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.db_name,
            charset=self.charset
        )

    def initialize_database(self):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                # Create books table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS books (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        title VARCHAR(255) NOT NULL,
                        book_id VARCHAR(50) UNIQUE NOT NULL,
                        author VARCHAR(255),
                        status VARCHAR(50) DEFAULT 'Available',
                        issuer_id VARCHAR(50),
                        course_code VARCHAR(50),
                        issue_date DATETIME,
                        return_date DATETIME
                    )
                """)

                # Create users table if it doesn't exist
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        password VARCHAR(255) NOT NULL,
                        is_admin BOOLEAN DEFAULT FALSE,
                        book_limit INT DEFAULT 3,
                        books_issued INT DEFAULT 0
                    )
                """)

                # Insert admin user if it doesn't exist
                cursor.execute("""
                    INSERT IGNORE INTO users (username, password, is_admin)
                    VALUES ('admin', 'admin123', TRUE)
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS book_requests (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        book_id VARCHAR(50),
                        user_id INT,
                        status VARCHAR(20) DEFAULT 'Pending',
                        request_date DATETIME,
                        approval_date DATETIME,
                        notes TEXT,
                        FOREIGN KEY (book_id) REFERENCES books(book_id),
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                """)

                connection.commit()
        finally:
            connection.close()
