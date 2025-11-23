"""
Session persistence management using cookies
"""
import streamlit as st
import extra_streamlit_components as stx
from datetime import datetime, timedelta
from auth.database import get_user_by_id

def get_cookie_manager():
    """
    Singleton pattern for CookieManager to avoid DuplicateElementKey error.
    """
    if "auth_cookie_manager_obj" in st.session_state:
        return st.session_state["auth_cookie_manager_obj"]
    
    # Initialize and store in session state
    cm = stx.CookieManager(key="auth_cookie_manager")
    st.session_state["auth_cookie_manager_obj"] = cm
    return cm

def check_auth_status():
    """
    Checks for existing session in cookies and restores login state.
    Returns: True if logged in (restored), False otherwise.
    """
    # 1. If already logged in state, return True
    if st.session_state.get("logged_in", False):
        return True

    # 2. Check cookies
    cm = get_cookie_manager()
    
    # Wait for the cookie manager to be ready
    # Note: On the very first load, cookies might be None until the component mounts
    cookies = cm.get_all()
    
    # Safety check if cookies is not None (component might be loading)
    if not cookies:
        return False
        
    user_id = cookies.get("user_token")

    if user_id:
        try:
            # Verify user exists in DB
            user = get_user_by_id(int(user_id))
            if user:
                st.session_state.logged_in = True
                st.session_state.user = user
                return True
        except:
            pass
            
    return False

def login_persist(user_id):
    """Sets the auth cookie to persist login"""
    cm = get_cookie_manager()
    # Cookie expires in 7 days
    expires = datetime.now() + timedelta(days=7)
    cm.set("user_token", str(user_id), expires_at=expires)

def logout_persist():
    """Clears the auth cookie"""
    cm = get_cookie_manager()
    cm.delete("user_token")