from database.connection import DatabaseConnection

class ActivityDAO:
    @staticmethod
    def log_activity(user_id, action_type, entity_type, entity_id=None, details=None):
        """
        Log a user activity for dashboard analytics

        Parameters:
        - user_id: ID of the user performing the action
        - action_type: Type of action (e.g., 'borrow', 'return', 'login', 'search')
        - entity_type: Type of entity being acted upon (e.g., 'book', 'user')
        - entity_id: ID of the entity
        - details: Additional details as a string
        """
        conn = DatabaseConnection.get_instance().get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO activity_logs
                    (user_id, action_type, entity_type, entity_id, details, timestamp)
                    VALUES (%s, %s, %s, %s, %s, NOW())
                """, (user_id, action_type, entity_type, entity_id, details))
                conn.commit()
                return cursor.lastrowid
        finally:
            conn.close()

    @staticmethod
    def get_recent_activities(user_id=None, limit=10):
        """Get recent activities for a user or all users"""
        conn = DatabaseConnection.get_instance().get_connection()
        try:
            with conn.cursor() as cursor:
                if user_id:
                    cursor.execute("""
                        SELECT a.*, u.username,
                               CASE
                                   WHEN a.entity_type = 'book' THEN b.title
                                   ELSE a.entity_id
                               END as entity_name
                        FROM activity_logs a
                        LEFT JOIN users u ON a.user_id = u.id
                        LEFT JOIN books b ON a.entity_id = b.book_id AND a.entity_type = 'book'
                        WHERE a.user_id = %s
                        ORDER BY a.timestamp DESC
                        LIMIT %s
                    """, (user_id, limit))
                else:
                    cursor.execute("""
                        SELECT a.*, u.username,
                               CASE
                                   WHEN a.entity_type = 'book' THEN b.title
                                   ELSE a.entity_id
                               END as entity_name
                        FROM activity_logs a
                        LEFT JOIN users u ON a.user_id = u.id
                        LEFT JOIN books b ON a.entity_id = b.book_id AND a.entity_type = 'book'
                        ORDER BY a.timestamp DESC
                        LIMIT %s
                    """, (limit,))

                return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def get_activity_stats(days=30):
        """Get activity statistics for the dashboard"""
        conn = DatabaseConnection.get_instance().get_connection()
        try:
            with conn.cursor() as cursor:
                # Get activity counts by type for the specified period
                cursor.execute("""
                    SELECT action_type, COUNT(*) as count
                    FROM activity_logs
                    WHERE timestamp > DATE_SUB(NOW(), INTERVAL %s DAY)
                    GROUP BY action_type
                    ORDER BY count DESC
                """, (days,))

                return cursor.fetchall()
        finally:
            conn.close()
