"""
Chat session management - CRUD operations for persistent chat library
"""

from auth.database import get_connection
from datetime import datetime

def create_chat_session(user_id, tab_name, first_message=""):
    """Create a new chat session and return session_id"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Generate title from first message (first 50 chars)
    title = first_message[:50] + "..." if len(first_message) > 50 else first_message
    if not title:
        title = f"New Chat - {datetime.now().strftime('%b %d, %Y %H:%M')}"
    
    cursor.execute("""
        INSERT INTO chat_sessions (user_id, tab_name, session_title, first_message)
        VALUES (?, ?, ?, ?)
    """, (user_id, tab_name, title, first_message))
    
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id

def get_user_sessions(user_id, tab_name=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, tab_name, session_title, created_at, updated_at, first_message
        FROM chat_sessions
        WHERE user_id=?
        ORDER BY updated_at DESC
    """, (user_id,))
    sessions = cursor.fetchall()
    conn.close()
    return sessions


def get_session_messages(session_id):
    """Get all messages for a specific chat session"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT role, content, timestamp
        FROM chat_history
        WHERE session_id=?
        ORDER BY timestamp ASC
    """, (session_id,))
    messages = cursor.fetchall()
    conn.close()
    return messages

def update_session_title(session_id, new_title):
    """Update chat session title"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE chat_sessions
        SET session_title=?, updated_at=CURRENT_TIMESTAMP
        WHERE id=?
    """, (new_title, session_id))
    conn.commit()
    conn.close()

def delete_session(session_id):
    """Delete a chat session and all its messages"""
    conn = get_connection()
    cursor = conn.cursor()
    # Delete messages first
    cursor.execute("DELETE FROM chat_history WHERE session_id=?", (session_id,))
    # Delete session
    cursor.execute("DELETE FROM chat_sessions WHERE id=?", (session_id,))
    conn.commit()
    conn.close()

def update_session_timestamp(session_id):
    """Update the 'updated_at' timestamp for a session"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE chat_sessions
        SET updated_at=CURRENT_TIMESTAMP
        WHERE id=?
    """, (session_id,))
    conn.commit()
    conn.close()
