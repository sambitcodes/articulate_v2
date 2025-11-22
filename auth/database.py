"""
Database setup and user authentication functions
"""

import sqlite3
import hashlib
from datetime import datetime

# Database connection (use check_same_thread=False for Streamlit)
DB_PATH = "users.db"

def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn

def init_database():
    """Initialize database tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Users table (existing)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            phone_number TEXT,
            profile_pic TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Chat sessions table (NEW)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            tab_name TEXT NOT NULL,
            session_title TEXT NOT NULL,
            first_message TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Chat history table (UPDATED - add session_id)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_id INTEGER NOT NULL,
            tab_name TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
        )
    """)
    
    conn.commit()
    conn.close()
    
    # Add missing columns for existing DBs
    add_missing_columns()

def add_missing_columns():
    """Add new columns to existing tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if session_id exists in chat_history
    columns = [row[1] for row in cursor.execute("PRAGMA table_info(chat_history);")]
    if "session_id" not in columns:
        try:
            cursor.execute("ALTER TABLE chat_history ADD COLUMN session_id INTEGER;")
        except:
            pass
    
    # Add phone_number and profile_pic if missing
    user_columns = [row[1] for row in cursor.execute("PRAGMA table_info(users);")]
    if "phone_number" not in user_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN phone_number TEXT;")
    if "profile_pic" not in user_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN profile_pic TEXT;")
    
    conn.commit()
    conn.close()


def add_missing_columns():
    """Add new columns to existing tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if session_id exists in chat_history
    columns = [row[1] for row in cursor.execute("PRAGMA table_info(chat_history);")]
    if "session_id" not in columns:
        try:
            cursor.execute("ALTER TABLE chat_history ADD COLUMN session_id INTEGER;")
        except:
            pass
    
    # Add phone_number and profile_pic if missing
    user_columns = [row[1] for row in cursor.execute("PRAGMA table_info(users);")]
    if "phone_number" not in user_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN phone_number TEXT;")
    if "profile_pic" not in user_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN profile_pic TEXT;")
    
    conn.commit()
    conn.close()


def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(full_name, username, email, password):
    """Register a new user"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (full_name, username, email, password) VALUES (?, ?, ?, ?)",
            (full_name, username, email, hash_password(password))
        )
        conn.commit()
        conn.close()
        return True, "Registration successful!"
    except sqlite3.IntegrityError as e:
        if "username" in str(e):
            return False, "Username already exists."
        elif "email" in str(e):
            return False, "Email already exists."
        return False, "Registration failed."

def login_user(username_or_email, password):
    """Authenticate user and return user data"""
    conn = get_connection()
    cursor = conn.cursor()
    pwd_hash = hash_password(password)
    
    cursor.execute(
        "SELECT id, full_name, username, email, phone_number, profile_pic FROM users WHERE (username=? OR email=?) AND password=?",
        (username_or_email, username_or_email, pwd_hash)
    )
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return True, {
            "id": user[0],
            "full_name": user[1],
            "username": user[2],
            "email": user[3],
            "phone_number": user[4],
            "profile_pic": user[5]
        }
    return False, None

def get_user_by_id(user_id):
    """Get user details by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, full_name, username, email, phone_number, profile_pic FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {
            "id": user[0],
            "full_name": user[1],
            "username": user[2],
            "email": user[3],
            "phone_number": user[4],
            "profile_pic": user[5]
        }
    return None
