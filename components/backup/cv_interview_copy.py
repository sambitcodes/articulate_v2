"""
CV Analysis & Interview Preparation Tab
"""

import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from utils.file_handler import validate_file, extract_text_from_file
from utils.chat_history import initialize_chat_history, add_message, display_chat_history, get_chat_history, format_chat_history_for_llm
from config import CV_INTERVIEW_MODELS, DEFAULT_CV_MODEL, SYSTEM_PROMPTS
import os

def cv_interview_tab():
    """CV Analysis & Interview Preparation Tab"""

    st.markdown("""
    <h4 style='text-align: left; color: #33FF33;'>
    📄👔 Thara Bhai JOBinder! 
    </h4>
    """,
    unsafe_allow_html=True)


    st.markdown("""
    <p style='text-align: left; color: #FF66B2;'>
       Upload your CV/Resume and get personalized interview questions,skill highlighting suggestions, and targeted preparation advice
    </p>
    """, 
    unsafe_allow_html=True)
    
    
    # Initialize session state
    tab_key = "cv_interview"
    initialize_chat_history(tab_key)
    
    # Sidebar Configuration
    with st.container(border = True):
    # Main Content Area
        choice_col, desc_col = st.columns([1, 2], gap="medium")
        
        with choice_col:
            # st.markdown("#### Upload Your Resume")
            uploaded_file = st.file_uploader(
                "Choose CV/Resume",
                type=["pdf", "docx", "txt"],
                key="cv_file_uploader"
            )
            
            if uploaded_file:
                is_valid, message = validate_file(uploaded_file)
                if not is_valid:
                    st.error(message)
                else:
                    st.success("File validated!")
                    resume_text = extract_text_from_file(uploaded_file)
                    if resume_text:
                        st.session_state['resume_text'] = resume_text
                        # st.markdown("**Preview (First 500 chars):**")
                        # st.text(resume_text[:500] + "...")
            
            model_col, temp_col = st.columns([1, 1], gap="medium")
            
            with model_col:
                selected_model_name = st.selectbox("Select AI Model",list(CV_INTERVIEW_MODELS.keys()),
                    index=list(CV_INTERVIEW_MODELS.keys()).index("Groq Compound (Best)"),key="cv_model_select")
                selected_model = CV_INTERVIEW_MODELS[selected_model_name]

            with temp_col:
                temperature = st.slider("Temperature",min_value=0.0,max_value=1.0,
                    value=0.3,step=0.1,key="cv_temperature")
            
        with desc_col:
            # st.markdown("#### Job Description")
            job_description = st.text_area(
                "Paste job description",
                height=200,
                key="cv_job_description"
            )

    with st.expander("⚠️🚫 Temperature Guidance", expanded=False):
        st.markdown(
            """
            <h5 style='color:#b8860b;'>How to use the temperature setting for Interview Prep:</h5>
            <span style='color:#b8860b;'>
            • <b>0.0–0.3: Most accurate and structured.</b> Use for company/role-specific and fact-based interview questions.<br>
            • <b>0.4–0.7: Balanced results.</b> Good for drawing subtle connections and some creativity in behavioral questions.<br>
            • <b>0.8–1.0: Highly creative,</b> but may hallucinate skills or scenarios.<br><br>
            <b>Tip:</b> Lower temperatures are best for technical, factual, or company-specific insights; higher temperatures for brainstorming or practicing open-ended responses.
            </span>
            """,
            unsafe_allow_html=True
        )



    # Action Buttons
    blank1,intercol,skillcol, blank2 = st.columns([2,1,1,2])
    
    with intercol:
        if st.button("Interview Questions", key="cv_gen_questions"):
            if 'resume_text' not in st.session_state:
                st.error("Upload resume first!")
            else:
                with st.spinner("Generating..."):
                    try:
                        llm = ChatGroq(
                            model=selected_model,
                            temperature=temperature,
                            groq_api_key=os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
                        )
                        
                        prompt_text = f"""Generate 10 targeted interview questions based on this resume:

RESUME:
{st.session_state['resume_text']}

{f'JOB DESCRIPTION:\\n{job_description}' if job_description else ''}

Include behavioral, technical, and role-specific questions."""
                        
                        response = llm.invoke(prompt_text)
                        questions = response.content
                        
                        st.session_state['interview_questions'] = questions
                        add_message(tab_key, "assistant", f"**Interview Questions:**\n\n{questions}")
                        st.success("Done!")
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    with skillcol:
        if st.button("Skill Highlights", key="cv_skill_highlights"):
            if 'resume_text' not in st.session_state:
                st.error("Upload resume first!")
            else:
                with st.spinner("Analyzing..."):
                    try:
                        llm = ChatGroq(
                            model=selected_model,
                            temperature=temperature,
                            groq_api_key=os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
                        )
                        
                        prompt_text = f"""Analyze this resume and provide:
1. Top 5 strongest skills to highlight
2. How to present each skill effectively
3. Questions to prepare for
4. Skills gaps to address

RESUME:
{st.session_state['resume_text']}"""
                        
                        response = llm.invoke(prompt_text)
                        highlights = response.content
                        
                        add_message(tab_key, "assistant", f"**Skill Highlights:**\n\n{highlights}")
                        st.success("Done!")
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    # Chat Interface
    st.markdown("---")
    # st.markdown("#### Chat with Career Coach")
    st.markdown("""
    <h4 style='text-align: left; color: #33FF33;'>
    👨‍🏫 Chat with Career Coach
    </h4>
    """,
    unsafe_allow_html=True)
    
    display_chat_history(tab_key)
    
    user_input = st.chat_input(
        "Ask your coach...",
        key="cv_chat_input"
    )
    
    if user_input:
        add_message(tab_key, "user", user_input)
        
        with st.spinner("Coach is thinking..."):
            try:
                llm = ChatGroq(
                    model=selected_model,
                    temperature=temperature,
                    groq_api_key=os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
                )
                
                context = f"""{SYSTEM_PROMPTS['cv_interview']}

RESUME: {st.session_state.get('resume_text', 'Not provided')}
JOB DESCRIPTION: {job_description if job_description else 'Not provided'}"""
                
                chat_history = format_chat_history_for_llm(tab_key)
                
                prompt = ChatPromptTemplate.from_messages([
                    ("system", context),
                    *[(msg["role"], msg["content"]) for msg in chat_history]
                ])
                
                response = llm.invoke(prompt.format_prompt().to_messages())
                assistant_response = response.content
                
                add_message(tab_key, "assistant", assistant_response)
                st.rerun()
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
