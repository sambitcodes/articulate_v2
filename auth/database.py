"""
Database setup and user authentication functions (PostgreSQL Version)
"""

import psycopg2
import hashlib
import os
import streamlit as st
from datetime import datetime

def get_connection():
    """Get database connection from Secrets or Environment"""
    db_url = os.getenv("DATABASE_URL") or st.secrets.get("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL not found in secrets or environment variables.")
    
    return psycopg2.connect(db_url)

def init_database():
    """Initialize database tables for PostgreSQL"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            full_name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            phone_number TEXT,
            profile_pic TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Chat sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            tab_name TEXT NOT NULL,
            session_title TEXT NOT NULL,
            first_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)
    
    # Chat history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            session_id INTEGER NOT NULL,
            tab_name TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
        );
    """)
    
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
            "INSERT INTO users (full_name, username, email, password) VALUES (%s, %s, %s, %s)",
            (full_name, username, email, hash_password(password))
        )
        conn.commit()
        conn.close()
        return True, "Registration successful!"
    except psycopg2.IntegrityError as e:
        error_msg = str(e)
        if "username" in error_msg:
            return False, "Username already exists."
        elif "email" in error_msg:
            return False, "Email already exists."
        return False, "Registration failed."
    except Exception as e:
        return False, f"Error: {str(e)}"

def login_user(username_or_email, password):
    """Authenticate user and return user data"""
    conn = get_connection()
    cursor = conn.cursor()
    pwd_hash = hash_password(password)
    
    cursor.execute(
        "SELECT id, full_name, username, email, phone_number, profile_pic FROM users WHERE (username=%s OR email=%s) AND password=%s",
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
    cursor.execute("SELECT id, full_name, username, email, phone_number, profile_pic FROM users WHERE id=%s", (user_id,))
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