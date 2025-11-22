"""
Login and Registration UI components
"""

import streamlit as st
from auth.database import register_user, login_user

def show_auth_page():
    """Display login/register page"""
    st.markdown("""
    <div style='text-align: center; padding: 40px 0 20px 0;'>
        <h1>👋 Welcome to articulAIte!</h1>
        <p style='font-size: 1.1em; color: #666;'>
            Your AI-powered career development assistant
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Mode selection
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        auth_mode = st.radio(
            "Select mode:",
            ["Login", "Register"],
            horizontal=True,
            label_visibility="collapsed"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if auth_mode == "Login":
        show_login_form()
    else:
        show_register_form()

def show_login_form():
    """Display login form"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔐 Login to Your Account")
        
        username_or_email = st.text_input(
            "Username or Email",
            placeholder="Enter your username or email",
            key="login_username"
        )
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_password"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        login_btn = st.button("🚀 Login", use_container_width=True, type="primary")
        
        if login_btn:
            if not username_or_email or not password:
                st.error("Please fill in all fields.")
            else:
                success, user_data = login_user(username_or_email, password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.user = user_data
                    st.success(f"Welcome back, {user_data['full_name']}! 🎉")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials. Please try again.")

def show_register_form():
    """Display registration form"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 📝 Create New Account")
        
        full_name = st.text_input(
            "Full Name",
            placeholder="Enter your full name",
            key="reg_fullname"
        )
        username = st.text_input(
            "Username",
            placeholder="Choose a username",
            key="reg_username"
        )
        email = st.text_input(
            "Email",
            placeholder="Enter your email",
            key="reg_email"
        )
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Choose a strong password",
            key="reg_password"
        )
        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Re-enter your password",
            key="reg_confirm"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        register_btn = st.button("✨ Register", use_container_width=True, type="primary")
        
        if register_btn:
            # Validation
            if not all([full_name, username, email, password, confirm_password]):
                st.error("Please fill in all fields.")
            elif password != confirm_password:
                st.error("❌ Passwords do not match!")
            elif len(password) < 6:
                st.error("❌ Password must be at least 6 characters long.")
            else:
                success, message = register_user(full_name, username, email, password)
                if success:
                    st.success("✅ " + message + " Please login now.")
                    st.balloons()
                else:
                    st.error("❌ " + message)
