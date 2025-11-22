"""
Chat Library UI Component - Similar to ChatGPT/Perplexity Library
"""

import streamlit as st
import uuid
from utils.chat_sessions import (
    get_user_sessions, 
    delete_session, 
    update_session_title,
    create_chat_session
)
from datetime import datetime

def show_chat_library(user_id):
    """Unified chat history sidebar for all tabs"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💬 Your Chats")

    # New Chat Button session_id to avoid duplicates
    unique_suffix = str(uuid.uuid4())[:8]
    if st.sidebar.button("➕ New Chat", use_container_width=True, key=f"new_chat_btn_{user_id}_{unique_suffix}"):
        new_session_id = create_chat_session(user_id, "All")
        st.session_state.current_session_id = new_session_id
        st.session_state.chat_messages = []
        st.rerun()

    # Get all sessions for this user (not per tab)
    sessions = get_user_sessions(user_id)

    if not sessions:
        st.sidebar.info("No chat history yet. Start a new conversation!")
        return

    st.sidebar.markdown("---")
    for session in sessions:
        session_id, tab_name, title, created_at, updated_at, first_msg = session

        updated = datetime.fromisoformat(str(updated_at))
        time_str = updated.strftime("%b %d, %H:%M")

        with st.sidebar.container():
            cols = st.columns([4, 1])
            with cols[0]:
                if st.button(f"💬 {title[:35]}...", key=f"session_{session_id}"):
                    load_session(session_id)
            with cols[1]:
                if st.button("🗑️", key=f"del_{session_id}"):
                    delete_session(session_id)
                    if st.session_state.get("current_session_id") == session_id:
                        # If deleted current session, create new one
                        new_id = create_chat_session(user_id, "All")
                        st.session_state.current_session_id = new_id
                        st.session_state.chat_messages = []
                    st.rerun()
            with st.sidebar.expander(f"✏️ Edit", expanded=False):
                new_title = st.text_input("Rename", value=title, key=f"rename_{session_id}")
                if st.button("Save", key=f"save_{session_id}"):
                    update_session_title(session_id, new_title)
                    st.rerun()


def load_session(session_id):
    """Load a chat session into current state"""
    from utils.chat_sessions import get_session_messages
    
    # Set current session
    st.session_state.current_session_id = session_id
    
    # Load messages from database
    messages = get_session_messages(session_id)
    
    # Convert to the EXACT format your tab expects
    # Check your tab's message format - it might use a different key name
    st.session_state.chat_messages = []
    for role, content, timestamp in messages:
        st.session_state.chat_messages.append({
            "role": role,
            "content": content
        })
    
    # Force rerun to show loaded messages
    st.rerun()

