import sqlite3
import logging
from pathlib import Path

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.__init__db()

    def __init__db(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact TEXT UNIQUE,
                status TEXT CHECK(status IN ('pending', 'sent', 'failed')) DEFAULT 'pending'
            )
            """      
        )

        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_contact_status ON messages (contact, status)")
        self.conn.commit()

    def reset_db(self):
        try:
            logging.info("Resetting database")
            self.cursor.execute("DELETE FROM messages")
            self.conn.commit()
        except sqlite3.OperationalError as e:
            logging.error(f"Error resetting database: {e}")

    def reset_failed_messages(self):
        try:
            logging.info("Resetting failed messages")
            self.cursor.execute("UPDATE messages SET status='pending' WHERE status='failed'")
            self.conn.commit()
        except sqlite3.OperationalError as e:
            logging.error(f"Error resetting failed messages: {e}")

    def was_message_sent(self, contact):
        self.cursor.execute("SELECT status FROM messages WHERE contact=?", (contact,))
        result = self.cursor.fetchone()
        return result and result[0] == "sent"

    
    def mark_message_status(self, contact, status):
        self.cursor.execute(
            """
            INSERT INTO messages (contact, status) VALUES (?, ?)
            ON CONFLICT(contact) DO UPDATE SET status=excluded.status
            """,
            (contact, status)
        )
        self.conn.commit()

    def close(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()
            logging.info("Database connection closed.")