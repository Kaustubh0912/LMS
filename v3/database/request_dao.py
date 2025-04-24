from database.connection import DatabaseConnection
from models.book_request import BookRequest

class BookRequestDAO:
    @staticmethod
    def create_request(request):
        conn = DatabaseConnection.get_instance().get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO book_requests (book_id, user_id, status, request_date, notes)
                    VALUES (%s, %s, %s, NOW(), %s)""",
                    (request.book_id, request.user_id, request.status, request.notes)
                )
                conn.commit()
                return cursor.lastrowid
        finally:
            conn.close()

    @staticmethod
    def get_request_by_id(request_id):
        conn = DatabaseConnection.get_instance().get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM book_requests WHERE id = %s", (request_id,))
                result = cursor.fetchone()
                if result:
                    return BookRequest(
                        id=result[0],
                        book_id=result[1],
                        user_id=result[2],
                        status=result[3],
                        request_date=result[4],
                        approval_date=result[5],
                        notes=result[6]
                    )
                return None
        finally:
            conn.close()

    @staticmethod
    def update_request_status(request_id, status):
        conn = DatabaseConnection.get_instance().get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """UPDATE book_requests SET status = %s, approval_date = NOW()
                    WHERE id = %s""",
                    (status, request_id)
                )
                conn.commit()
                return cursor.rowcount > 0
        finally:
            conn.close()

    @staticmethod
    def get_pending_requests():
        conn = DatabaseConnection.get_instance().get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        br.id,
                        b.title,
                        b.book_id,
                        u.username,
                        u.id as user_id,
                        br.request_date,
                        br.status,
                        u.books_issued,
                        u.book_limit,
                        br.notes
                    FROM book_requests br
                    JOIN books b ON br.book_id = b.book_id
                    JOIN users u ON br.user_id = u.id
                    WHERE br.status = 'Pending'
                    ORDER BY br.request_date DESC
                """)
                return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def get_requests_by_user(user_id):
        conn = DatabaseConnection.get_instance().get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        br.id,
                        b.title,
                        b.book_id,
                        br.request_date,
                        br.status,
                        br.approval_date,
                        br.notes
                    FROM book_requests br
                    JOIN books b ON br.book_id = b.book_id
                    WHERE br.user_id = %s
                    ORDER BY br.request_date DESC
                """, (user_id,))
                return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def get_request_statistics():
        conn = DatabaseConnection.get_instance().get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT status, COUNT(*)
                    FROM book_requests
                    GROUP BY status
                """)
                return dict(cursor.fetchall())
        finally:
            conn.close()
    
    @staticmethod
    def get_request_history():
        conn = DatabaseConnection.get_instance().get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        br.id,
                        b.title,
                        b.book_id,
                        u.username,
                        u.id as user_id,
                        br.request_date,
                        br.status,
                        u.books_issued,
                        u.book_limit,
                        br.approval_date,
                        br.notes
                    FROM book_requests br
                    JOIN books b ON br.book_id = b.book_id
                    JOIN users u ON br.user_id = u.id
                    WHERE br.status != 'Pending'
                    ORDER BY br.request_date DESC
                """)
                return cursor.fetchall()
        finally:
            conn.close()