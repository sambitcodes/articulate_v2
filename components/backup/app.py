"""
Main Streamlit application - articulAIte
AI-Powered Career Development Assistant using LangChain and Groq
"""

import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import tab modules
from tabs.cv_interview import cv_interview_tab
from tabs.code_explainer import code_explainer_tab
from tabs.article_generator import article_generator_tab
from tabs.study_plan import study_plan_tab

# Configure Streamlit page
st.set_page_config(
    page_title="articulAIte 🤖",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #1f77e8;
    }
    .tab-description {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# Check API Key
def check_api_key():
    api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
    if not api_key:
        st.error(
            "🔑 GROQ_API_KEY not found!\n\n"
            "**Local Setup:** Add `GROQ_API_KEY=your_key` to `.env` file\n"
            "**Streamlit Cloud:** Add to App settings → Secrets"
        )
        return False
    return True

# Main App
def main():
    # Header
    st.markdown(
    """
    <h1 style='text-align: center; color: white;'>
        🎯 articul<span style='color: #FF9933;'>AI</span>te 🤖 
    </h1>
    """, 
    unsafe_allow_html=True
)

    st.markdown(
        """
        <p style='text-align: center; color: #666;'>
        Interviewer 👔 | Coder 👨‍💻| Writer ✒️| Planner 🗓️ - Powered by <span style='color: #4169E1;'>AI</span> 
        </p>
        """, 
        unsafe_allow_html=True
    )
    # st.markdown("<h1 class='main-header'>🎯 articulAIte 🤖</h1>", unsafe_allow_html=True)
    # st.markdown(
    #     "<p style='text-align: center; color: #666;'>"
    #     "Interviewer 👔 | Coder 👨‍💻| Writer ✒️| Planner 🗓️ - Powered by AI"
    #     "</p>",
    #     unsafe_allow_html=True
    # )
    
    # Check API Key
    if not check_api_key():
        st.stop()
    
    # Sidebar
    # st.sidebar.title("📋 Navigation")
    # st.sidebar.markdown("---")
    
    # st.sidebar.markdown("""
    # ### About articulAIte
    
    # An AI-powered assistant leveraging LangChain and Groq to help you:
    # - 📄 Prepare for interviews
    # - 💻 Solve coding problems
    # - 📝 Generate content
    # - 📚 Create study plans
    
    # **Chat with AI** in each tab!
    # """)
    
    # st.sidebar.markdown("---")
    # st.sidebar.markdown(
    #     "**Powered by:** Groq API | **Built with:** Streamlit & LangChain"
    # )
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📄👔 CV & Interview",
        "👨‍💻⚛ Code Explainer",
        "✒️📜 Article Generator",
        "📋🗓️ Study Plan"
    ])
    
    with tab1:
        cv_interview_tab()
    
    with tab2:
        code_explainer_tab()
    
    with tab3:
        article_generator_tab()
    
    with tab4:
        study_plan_tab()

    st.markdown("---")
    st.markdown("""
    <div style='padding:20px 0 0 0; color:#358; font-size: 1.04em; text-align: center;'>
    <h5 style='text-align: center;'>Empower Your Love for learning with AI</h4>
    <p style='text-align: center;'>
    Powered by <b>Groq API</b>  &nbsp;&nbsp; | &nbsp;&nbsp; Built with ❤️ using <b>LangChain</b> 
    </p>
    <a href="https://github.com/sambitcodes" target="_blank" style="text-decoration:none;">
      <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/github/github-original.svg" 
        style="vertical-align:middle; margin-bottom: 3px;" height="22" />
      <span style="font-size:1em; margin-left:6px; vertical-align:middle; text-align: center;">sambitcodes ©</span>
    </a>
    """, unsafe_allow_html=True)
    # <h6 style='text-align: center;'>An AI-powered assistant leveraging <b>LangChain</b> and <b>Groq</b> to help you:</h5>
    # <ul style='text-align: center;'>
    #  📄 <b>Prepare for interviews</b>
    #  💻 <b>Solve coding problems</b>
    #  📝 <b>Generate content</b>
    #  📚 <b>Create study plans</b>
    #  💬 <b>Chat with AI in each tab!</b>
    # </ul>

if __name__ == "__main__":
    main()
