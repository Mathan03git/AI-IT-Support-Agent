
import sqlite3
from pathlib import Path
from datetime import datetime


# ==========================================
# DATABASE CONFIGURATION
# ==========================================

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_DIR / "data" / "conversations.db"


# ==========================================
# DATABASE INITIALIZATION
# ==========================================

def init_db():

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with sqlite3.connect(DATABASE_PATH) as connection:

        cursor = connection.cursor()

        # Conversation history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        # Log analysis history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS log_analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                analysis TEXT NOT NULL,
                error_count INTEGER DEFAULT 0,
                warning_count INTEGER DEFAULT 0,
                info_count INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
        """)

        connection.commit()


# ==========================================
# SAVE CONVERSATION
# ==========================================

def save_conversation(question, answer):

    with sqlite3.connect(DATABASE_PATH) as connection:

        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO conversations
            (question, answer, created_at)
            VALUES (?, ?, ?)
        """, (
            question,
            answer,
            datetime.now().astimezone().isoformat(
                timespec="seconds"
            )
        ))

        connection.commit()


# ==========================================
# RETRIEVE CONVERSATION HISTORY
# ==========================================

def get_conversations():

    with sqlite3.connect(DATABASE_PATH) as connection:

        connection.row_factory = sqlite3.Row

        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, question, answer, created_at
            FROM conversations
            ORDER BY id DESC
        """)

        conversations = [
            dict(row)
            for row in cursor.fetchall()
        ]

        return conversations


# ==========================================
# SAVE LOG ANALYSIS
# ==========================================

def save_log_analysis(
    filename,
    analysis,
    error_count,
    warning_count,
    info_count
):

    with sqlite3.connect(DATABASE_PATH) as connection:

        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO log_analyses
            (
                filename,
                analysis,
                error_count,
                warning_count,
                info_count,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            filename,
            analysis,
            error_count,
            warning_count,
            info_count,
            datetime.now().astimezone().isoformat(
                timespec="seconds"
            )
        ))

        connection.commit()


# ==========================================
# RETRIEVE LOG ANALYSIS HISTORY
# ==========================================

def get_log_analyses():

    with sqlite3.connect(DATABASE_PATH) as connection:

        connection.row_factory = sqlite3.Row

        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                filename,
                analysis,
                error_count,
                warning_count,
                info_count,
                created_at
            FROM log_analyses
            ORDER BY id DESC
        """)

        analyses = [
            dict(row)
            for row in cursor.fetchall()
        ]

        return analyses


# ==========================================
# MAIN
# ==========================================

if __name__ == "__main__":

    init_db()

    print("SQLite database initialized successfully!")

    print(f"Database location: {DATABASE_PATH}")

    print("Conversation history table: Ready")

    print("Log analysis history table: Ready")
