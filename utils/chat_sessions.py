"""
Chat session management - CRUD operations for persistent chat library
"""

from auth.database import get_connection
from datetime import datetime

def create_chat_session(user_id, tab_name, first_message=""):
    """Create a new chat session and return session_id"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Generate title
    if first_message:
        title = first_message[:50] + "..." if len(first_message) > 50 else first_message
    else:
        title = "New Chat"
    
    cursor.execute("""
        INSERT INTO chat_sessions (user_id, tab_name, session_title, first_message)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (user_id, tab_name, title, first_message))
    
    session_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return session_id

def get_user_sessions(user_id, tab_name=None, limit=10):
    """Get recent sessions for a user/tab"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if tab_name:
        cursor.execute("""
            SELECT id, tab_name, session_title, created_at, updated_at, first_message
            FROM chat_sessions
            WHERE user_id=%s AND tab_name=%s
            ORDER BY updated_at DESC
            LIMIT %s
        """, (user_id, tab_name, limit))
    else:
        cursor.execute("""
            SELECT id, tab_name, session_title, created_at, updated_at, first_message
            FROM chat_sessions
            WHERE user_id=%s
            ORDER BY updated_at DESC
            LIMIT %s
        """, (user_id, limit))
        
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
        WHERE session_id=%s
        ORDER BY timestamp ASC
    """, (session_id,))
    messages = cursor.fetchall()
    conn.close()
    return messages

def update_session_title_if_new(session_id, first_message):
    """Update title if it is still 'New Chat'"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check current title
    cursor.execute("SELECT session_title FROM chat_sessions WHERE id=%s", (session_id,))
    result = cursor.fetchone()
    
    if result and result[0] == "New Chat":
        new_title = first_message[:50] + "..." if len(first_message) > 50 else first_message
        cursor.execute("""
            UPDATE chat_sessions
            SET session_title=%s, updated_at=CURRENT_TIMESTAMP
            WHERE id=%s
        """, (new_title, session_id))
        conn.commit()
    
    conn.close()

def update_session_title(session_id, new_title):
    """Manually update chat session title"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE chat_sessions
        SET session_title=%s, updated_at=CURRENT_TIMESTAMP
        WHERE id=%s
    """, (new_title, session_id))
    conn.commit()
    conn.close()

def delete_session(session_id):
    """Delete a chat session and all its messages"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_history WHERE session_id=%s", (session_id,))
    cursor.execute("DELETE FROM chat_sessions WHERE id=%s", (session_id,))  
    conn.commit()
    conn.close()