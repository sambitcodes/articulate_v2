import streamlit as st
from auth.database import get_connection, get_user_by_id
from auth.session_manager import logout_persist
import os

PROFILE_IMG_FOLDER = "profile_images"

def update_user_profile(user_id, full_name, email, phone, pic_url):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users SET full_name=%s, email=%s, phone_number=%s, profile_pic=%s
        WHERE id=%s
    """, (full_name, email, phone, pic_url, user_id))
    conn.commit()
    conn.close()

def show_profile_page():
    user = st.session_state.user
    st.markdown("<h2 style='text-align:center'>🧑‍💼 Profile</h2>", unsafe_allow_html=True)
    pic_path = user.get("profile_pic")
    if pic_path and os.path.exists(pic_path):
        st.image(pic_path, width=120)
    else:
        st.image("https://ui-avatars.com/api/?name=" + user["username"], width=120)

    # Editable fields
    full_name = st.text_input("Full Name", value=user["full_name"])
    email = st.text_input("Email", value=user["email"])
    phone = st.text_input("Phone Number", value=user.get("phone_number", ""))
    uploaded_profile_pic = st.file_uploader("Upload Profile Picture", type=["jpg", "jpeg", "png"])
    new_pic_path = pic_path

    if uploaded_profile_pic:
        # Ensure folder exists
        if not os.path.exists(PROFILE_IMG_FOLDER):
            os.makedirs(PROFILE_IMG_FOLDER)
        # Save uploaded image
        ext = uploaded_profile_pic.name.split('.')[-1]
        local_path = os.path.join(PROFILE_IMG_FOLDER, f"user_{user['id']}.{ext}")
        with open(local_path, "wb") as f:
            f.write(uploaded_profile_pic.getbuffer())
        new_pic_path = local_path  # Store path to save when profile saved
        st.image(local_path, width=120)

    if st.button("Save Profile", key="profile_save"):
        update_user_profile(user["id"], full_name, email, phone, new_pic_path)
        user_updated = get_user_by_id(user["id"])
        user_updated["profile_pic"] = new_pic_path
        user_updated["phone_number"] = phone
        st.session_state.user = user_updated
        st.success("Profile updated!")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Logout", type="primary"):
        logout_persist()
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.profile_mode = False
        time.sleep(0.5)
        st.rerun()

    if st.button("⬅️ Back to Home", key="back_to_home"):
        st.session_state.profile_mode = False
        st.rerun()