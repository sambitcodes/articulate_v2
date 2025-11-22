"""
Chat history management utilities
"""

import streamlit as st
from datetime import datetime
from config import CHAT_MAX_HISTORY

def initialize_chat_history(key):
    """Initialize chat history in session state"""
    if key not in st.session_state:
        st.session_state[key] = []

def add_message(key, role, content):
    """Add message to chat history"""
    initialize_chat_history(key)
    st.session_state[key].append({
        "role": role,
        "content": content,
        "timestamp": datetime.now()
    })
    
    # Limit history size
    if len(st.session_state[key]) > CHAT_MAX_HISTORY:
        st.session_state[key] = st.session_state[key][-CHAT_MAX_HISTORY:]

def get_chat_history(key):
    """Get chat history"""
    initialize_chat_history(key)
    return st.session_state[key]

def clear_chat_history(key):
    """Clear chat history"""
    if key in st.session_state:
        st.session_state[key] = []

def format_chat_history_for_llm(key):
    """Format chat history for LLM consumption"""
    history = get_chat_history(key)
    formatted = []
    for msg in history:
        formatted.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    return formatted

def display_chat_history(key):
    """Display chat history in Streamlit"""
    history = get_chat_history(key)
    for msg in history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
