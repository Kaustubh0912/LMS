from database.connection import DatabaseConnection
from models.book import Book

class BookDAO:
    @staticmethod
    def get_all_books():
        conn = DatabaseConnection.get_instance().get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM books")
                results = cursor.fetchall()
                return [Book(
                    id=row[0],
                    title=row[1],
                    book_id=row[2],
                    author=row[3],
                    status=row[4],
                    issuer_id=row[5],
                    course_code=row[6],
                    issue_date=row[7],
                    return_date=row[8]
                ) for row in results]
        finally:
            conn.close()

    @staticmethod
    def get_book_by_id(book_id):
        conn = DatabaseConnection.get_instance().get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
                result = cursor.fetchone()
                print(f"get_book_by_id - result: {result}")
                
                if result:
                    return Book(
                        id=result[0],
                        title=result[1],
                        book_id=result[2],
                        author=result[3],
                        status=result[4],
                        issuer_id=result[5],
                        course_code=result[6],
                        issue_date=result[7],
                        return_date=result[8]
                    )
                return None
        finally:
            conn.close()
    @staticmethod
    def get_books_with_request_status(user_id=None):
        conn = DatabaseConnection.get_instance().get_connection()
        try:
            with conn.cursor() as cursor:
                query = """
                    SELECT b.*, r.status as request_status, u.username as issuer_name
                    FROM books b
                    LEFT JOIN book_requests r ON b.book_id = r.book_id AND r.user_id = %s
                    LEFT JOIN users u ON b.issuer_id = u.id
                """
                cursor.execute(query, (user_id,))
                return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def search_books(search_text, user_id=None):
        """
        Enhanced search books function that searches across multiple fields
        
        Parameters:
            search_text (str): Text to search for
            user_id (int, optional): User ID for request status
        """
        conn = DatabaseConnection.get_instance().get_connection()
        try:
            with conn.cursor() as cursor:
                query = """
                    SELECT b.*, r.status as request_status, u.username as issuer_name
                    FROM books b
                    LEFT JOIN book_requests r ON b.book_id = r.book_id AND r.user_id = %s
                    LEFT JOIN users u ON b.issuer_id = u.id
                    WHERE b.title LIKE %s
                    OR b.book_id LIKE %s
                    OR b.author LIKE %s
                    OR b.course_code LIKE %s
                """
                cursor.execute(query, (
                    user_id,
                    f"%{search_text}%",
                    f"%{search_text}%",
                    f"%{search_text}%",
                    f"%{search_text}%"
                ))
                return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def filter_books(filter_option, user_id=None):
        conn = DatabaseConnection.get_instance().get_connection()
        try:
            with conn.cursor() as cursor:
                if filter_option == "Available Books":
                    query = """
                        SELECT b.*, r.status as request_status, u.username as issuer_name
                        FROM books b
                        LEFT JOIN book_requests r ON b.book_id = r.book_id AND r.user_id = %s
                        LEFT JOIN users u ON b.issuer_id = u.id
                        WHERE b.status = 'Available'
                    """
                    cursor.execute(query, (user_id,))
                elif filter_option == "My Requests":
                    query = """
                        SELECT b.*, r.status as request_status, u.username as issuer_name
                        FROM books b
                        INNER JOIN book_requests r ON b.book_id = r.book_id
                        LEFT JOIN users u ON b.issuer_id = u.id
                        WHERE r.user_id = %s
                    """
                    cursor.execute(query, (user_id,))
                else:  # All Books
                    query = """
                        SELECT b.*, r.status as request_status, u.username as issuer_name
                        FROM books b
                        LEFT JOIN book_requests r ON b.book_id = r.book_id AND r.user_id = %s
                        LEFT JOIN users u ON b.issuer_id = u.id
                    """
                    cursor.execute(query, (user_id,))

                return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def add_book(book):
        conn = DatabaseConnection.get_instance().get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO books (title, book_id, author, status, course_code) VALUES (%s, %s, %s, %s, %s)",
                    (book.title, book.book_id, book.author, book.status, book.course_code)
                )
                conn.commit()
                return True
        finally:
            conn.close()

    @staticmethod
    def update_book(book):
        conn = DatabaseConnection.get_instance().get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """UPDATE books
                    SET title = %s, author = %s, status = %s, course_code = %s
                    WHERE book_id = %s""",
                    (book.title, book.author, book.status, book.course_code, book.book_id)
                )
                conn.commit()
                return True
        finally:
            conn.close()

    @staticmethod
    def delete_book(book_id):
        conn = DatabaseConnection.get_instance().get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM book_requests WHERE book_id = %s", (book_id,))
                cursor.execute("DELETE FROM books WHERE book_id = %s", (book_id,))
                conn.commit()
                return True
        finally:
            conn.close()

    @staticmethod
    def return_book(book_id):
        conn = DatabaseConnection.get_instance().get_connection()
        try:
            with conn.cursor() as cursor:
                # Step 1: Get the current book status and issuer ID with proper debugging
                cursor.execute("SELECT id, status, issuer_id FROM books WHERE book_id = %s", (book_id,))
                result = cursor.fetchone()
                
                print(f"Return book - Found book: {result}")
                
                if not result:
                    print(f"Return book error: Book with ID {book_id} not found")
                    return False
                    
                book_db_id, status, issuer_id = result
                    
                if status != 'Issued':
                    print(f"Return book error: Book status is {status}, not 'Issued'")
                    return False
                
                if not issuer_id:
                    print(f"Return book error: Book has no issuer_id")
                    return False
                    
                # Step 2: Update book status
                print(f"Updating book status to Available for book_id: {book_id}")
                cursor.execute(
                    """UPDATE books 
                    SET status = 'Available', 
                        issuer_id = NULL,
                        issue_date = NULL, 
                        return_date = NULL 
                    WHERE book_id = %s""",
                    (book_id,)
                )
                rows_affected = cursor.rowcount
                print(f"Book update rows affected: {rows_affected}")
                
                # Step 3: Update user's books_issued count
                print(f"Updating books_issued count for user ID: {issuer_id}")
                cursor.execute(
                    "UPDATE users SET books_issued = GREATEST(books_issued - 1, 0) WHERE id = %s",
                    (issuer_id,)
                )
                user_rows_affected = cursor.rowcount
                print(f"User update rows affected: {user_rows_affected}")
                
                # Step 4: Update related book request status
                print(f"Updating related book request status for book_id: {book_id}")
                cursor.execute(
                    "UPDATE book_requests SET status = 'Returned' WHERE book_id = %s AND status = 'Approved'",
                    (book_id,)
                )
                request_rows_affected = cursor.rowcount
                print(f"Request update rows affected: {request_rows_affected}")
                
                conn.commit()
                print(f"Book return operation successful for book_id: {book_id}")
                return True
        except Exception as e:
            print(f"Error returning book: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()