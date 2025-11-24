"""
Chat Library UI Component - Right Column Integration
Optimized with Session State Caching to prevent slow DB reloads
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
    Uses session state caching to avoid DB latency on every rerun.
    """
    with container:
        st.markdown(f"### 🗄️ Library")
        st.caption(f"History: {tab_name}")

        # Keys
        session_id_key = f"session_id_{tab_key}"
        messages_key = f"messages_{tab_key}"
        
        # Cache Key: We store the list of sessions in session_state to avoid 
        # hitting the Supabase DB on every single interaction (dropdown change, typing, etc.)
        cache_key = f"cached_sessions_list_{tab_key}"

        # Function to force-refresh the cache (e.g., after delete/create)
        def refresh_cache():
            if cache_key in st.session_state:
                del st.session_state[cache_key]

        # New Chat Button
        unique_suffix = str(uuid.uuid4())[:8]
        if st.button("➕ New Chat", use_container_width=True, key=f"new_chat_{tab_key}_{unique_suffix}"):
            # Create new session in DB immediately
            new_id = create_chat_session(user_id, tab_name)
            # Update State
            st.session_state[session_id_key] = new_id
            st.session_state[messages_key] = []
            
            # Invalidate cache so the new chat appears in the list next time
            refresh_cache()
            st.rerun()

        # --- CACHING LOGIC START ---
        # Only fetch from DB if we don't have it in memory
        if cache_key not in st.session_state:
            with st.spinner("Loading history..."):
                st.session_state[cache_key] = get_user_sessions(user_id, tab_name=tab_name, limit=10)
        
        sessions = st.session_state[cache_key]
        # --- CACHING LOGIC END ---

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
                # Truncate title for UI
                display_title = title if len(title) < 25 else title[:25] + "..."
                if st.button(f"💬 {display_title}", key=f"load_{tab_key}_{sess_id}", help=f"{title} ({updated_at})", use_container_width=True, type=button_style):
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
                    
                    # Force refresh of the list
                    refresh_cache()
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