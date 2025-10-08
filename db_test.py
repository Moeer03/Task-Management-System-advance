import sqlite3
import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv("config.env")

DB_FILE = os.getenv("DB_FILE")

# --- Global DB Connection ---
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()



def init_db():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            completion_flag BOOLEAN DEFAULT 0
        )
    """)
    conn.commit()
    return "Database Connected.........."

def create_task_in_db(task):
    cursor.execute("""
        INSERT INTO tasks (title, description, completion_flag)
        VALUES (?, ?, ?)
    """, (task.title, task.description, task.completion_flag))
    conn.commit()
    return cursor.lastrowid

def display_all_tasks(completed):
    if completed is None:
        cursor.execute("SELECT * FROM tasks")
    else:
        cursor.execute("SELECT * FROM tasks WHERE completion_flag = ?", (int(completed),))
    return cursor.fetchall()

def display_one_task_in_db(task_id):
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    return cursor.fetchone()

def update_flag_in_db(task_id, completion_flag):
    cursor.execute(
        "UPDATE tasks SET completion_flag = ? WHERE id = ?",
        (int(completion_flag), task_id)
    )
    conn.commit()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    return cursor.fetchone()

def delete_task_in_db(task_id):
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    return cursor.rowcount

def update_task_in_db(task_id, title, description):
    cursor.execute("SELECT title, description FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    if not row:
        return None

    current_title, current_description = row
    new_title = title if title is not None else current_title
    new_description = description if description is not None else current_description

    cursor.execute("""
        UPDATE tasks SET title = ?, description = ? WHERE id = ?
    """, (new_title, new_description, task_id))
    conn.commit()

    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    return cursor.fetchone()

def close_db():
    if cursor:
        cursor.close()
    if conn:
        conn.close()
    print("Database connection closed.")
