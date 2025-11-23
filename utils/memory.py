"""
Chat history storage and retrieval for authenticated users
"""

from auth.database import get_connection
# from utils.chat_sessions import update_session_timestamp

def save_chat_message(user_id, session_id, tab_name, role, content):
    """Save a single chat message to database with session_id"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chat_history (user_id, session_id, tab_name, role, content) VALUES (%s, %s, %s, %s, %s)",      
        (user_id, session_id, tab_name, role, content)
    )
    conn.commit()
    conn.close()
    
    # Update session timestamp
    update_session_timestamp(session_id)

def get_chat_history(user_id, tab_name=None, limit=50):
    """Retrieve chat history for a user (legacy - for backward compatibility)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if tab_name:
        cursor.execute(
            "SELECT role, content, timestamp FROM chat_history WHERE user_id=%s AND tab_name=%s ORDER BY timestamp DESC LIMIT %s",
            (user_id, tab_name, limit)
        )
    else:
        cursor.execute(
            "SELECT tab_name, role, content, timestamp FROM chat_history WHERE user_id=%s ORDER BY timestamp DESC LIMIT %s",
            (user_id, limit)
        )
    
    results = cursor.fetchall()
    conn.close()
    return results[::-1] # Reverse to get chronological order

def get_all_sessions(user_id):
    """Get all chat sessions for a user (grouped by tab and date)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT DISTINCT tab_name, DATE(timestamp) as chat_date, COUNT(*) as message_count
        FROM chat_history 
        WHERE user_id=%s    
        GROUP BY tab_name, chat_date 
        ORDER BY timestamp DESC""",
        (user_id,)
    )
    results = cursor.fetchall()
    conn.close()
    return results

def delete_chat_history(user_id, tab_name=None):
    """Delete chat history for a user"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if tab_name:
        cursor.execute("DELETE FROM chat_history WHERE user_id=%s AND tab_name=%s", (user_id, tab_name))
    else:
        cursor.execute("DELETE FROM chat_history WHERE user_id=%s", (user_id,))
    
    conn.commit()
    conn.close()
