"""
Chat Library UI Component - Right Column Integration
"""

import streamlit as st
import uuid
from utils.chat_sessions import (
    get_user_sessions, 
    delete_session, 
    create_chat_session,
    get_session_messages
)
from datetime import datetime

def show_chat_library(user_id, tab_name, tab_key, container):
    """
    Unified chat history list for the right column.
    """
    with container:
        st.markdown(f"### 🗄️ Library")
        st.caption(f"History: {tab_name}")

        # Keys
        session_id_key = f"session_id_{tab_key}"
        messages_key = f"messages_{tab_key}"

        # New Chat Button
        unique_suffix = str(uuid.uuid4())[:8]
        if st.button("➕ New Chat", use_container_width=True, key=f"new_chat_{tab_key}_{unique_suffix}"):
            # Create new session in DB immediately
            new_id = create_chat_session(user_id, tab_name)
            # Update State
            st.session_state[session_id_key] = new_id
            st.session_state[messages_key] = []
            st.rerun()

        # Get sessions
        sessions = get_user_sessions(user_id, tab_name=tab_name, limit=10)

        if not sessions:
            st.info("No saved chats.")
            return

        st.markdown("---")
        
        # Current Active Session ID
        active_id = st.session_state.get(session_id_key)

        for session in sessions:
            sess_id, _, title, _, updated_at, _ = session
            
            # Highlight active
            is_active = (active_id == sess_id)
            
            # Styling for active vs inactive
            button_style = "primary" if is_active else "secondary"
            
            # Layout
            c1, c2 = st.columns([4, 1])
            with c1:
                # Load Button
                if st.button(f"💬 {title}", key=f"load_{tab_key}_{sess_id}", help=str(updated_at), use_container_width=True, type=button_style):
                    load_session(sess_id, tab_key)
            
            with c2:
                # Delete Button
                if st.button("🗑️", key=f"del_{tab_key}_{sess_id}"):
                    delete_session(sess_id)
                    # If deleted active, reset
                    if is_active:
                        new_id = create_chat_session(user_id, tab_name)
                        st.session_state[session_id_key] = new_id
                        st.session_state[messages_key] = []
                    st.rerun()

def load_session(session_id, tab_key):
    """Load a chat session into the state"""
    session_id_key = f"session_id_{tab_key}"
    messages_key = f"messages_{tab_key}"
    
    # 1. Update Session ID
    st.session_state[session_id_key] = session_id
    
    # 2. Fetch Messages from DB
    db_messages = get_session_messages(session_id)
    
    # 3. Update Messages State
    loaded_msgs = []
    for role, content, _ in db_messages:
        loaded_msgs.append({
            "role": role,
            "content": content
        })
    st.session_state[messages_key] = loaded_msgs
    
    # 4. Rerun to reflect changes
    st.rerun()