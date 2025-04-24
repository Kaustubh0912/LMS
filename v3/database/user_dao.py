from database.connection import DatabaseConnection
from models.user import User

class UserDAO:
    @staticmethod
    def get_by_credentials(username, password):
        connection = DatabaseConnection.get_instance().get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM users WHERE username = %s AND password = %s",
                    (username, password)
                )
                user_data = cursor.fetchone()
                if user_data:
                    return User(
                        id=user_data[0],
                        username=user_data[1],
                        password=user_data[2],
                        is_admin=user_data[3],
                        book_limit=user_data[4],
                        books_issued=user_data[5]
                    )
                return None
        finally:
            connection.close()

    @staticmethod
    def get_all_users():
        connection = DatabaseConnection.get_instance().get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users")
                users = cursor.fetchall()
                return [User(
                    id=user[0],
                    username=user[1],
                    password=user[2],
                    is_admin=user[3],
                    book_limit=user[4],
                    books_issued=user[5]
                ) for user in users]
        finally:
            connection.close()

    @staticmethod
    def add_user(user):
        connection = DatabaseConnection.get_instance().get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO users (username, password, is_admin, book_limit) VALUES (%s, %s, %s, %s)",
                    (user.username, user.password, user.is_admin, user.book_limit)
                )
                connection.commit()
                return True
        finally:
            connection.close()

    @staticmethod
    def delete_user(user_id):
        connection = DatabaseConnection.get_instance().get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM book_requests WHERE user_id = %s", (user_id,))
                cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
                connection.commit()
                return True
        finally:
            connection.close()

    @staticmethod
    def update_book_limit(user_id, new_limit):
        connection = DatabaseConnection.get_instance().get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE users SET book_limit = %s WHERE id = %s",
                    (new_limit, user_id)
                )
                connection.commit()
                return True
        finally:
            connection.close()
