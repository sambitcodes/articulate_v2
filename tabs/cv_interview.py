"""
CV Analysis & Interview Preparation Tab
"""

import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from utils.file_handler import validate_file, extract_text_from_file
from utils.memory import save_chat_message
from utils.chat_sessions import create_chat_session, get_user_sessions, get_session_messages, update_session_title_if_new
from components.chat_library import show_chat_library
from config import CV_INTERVIEW_MODELS, SYSTEM_PROMPTS
import os

def cv_interview_tab():
    """CV Analysis & Interview Preparation Tab"""
    
    user_id = st.session_state.user["id"]
    tab_name = "CV Interview"
    tab_key = "cv_interview"

    session_id_key = f"session_id_{tab_key}"
    messages_key = f"messages_{tab_key}"

    # --- Initialization ---
    if session_id_key not in st.session_state:
        sessions = get_user_sessions(user_id, tab_name, limit=1)
        if sessions:
            latest_session = sessions[0]
            st.session_state[session_id_key] = latest_session[0]
            db_msgs = get_session_messages(latest_session[0])
            st.session_state[messages_key] = [{"role": r, "content": c} for r, c, _ in db_msgs]
        else:
            new_id = create_chat_session(user_id, tab_name)
            st.session_state[session_id_key] = new_id
            st.session_state[messages_key] = []
            
    if messages_key not in st.session_state:
        st.session_state[messages_key] = []

    # --- Layout ---
    main_col, lib_col = st.columns([4, 1])
    show_chat_library(user_id, tab_name, tab_key, lib_col)

    with main_col: 
        st.markdown("""<h4 style='text-align: left; color: #33FF33;'>📄👔 Thara Bhai JOBinder! </h4>""",unsafe_allow_html=True)
        st.markdown("""<p style='text-align: left; color: #FF66B2;'>
        Upload your CV/Resume and get personalized interview questions, skill highlighting suggestions, and targeted preparation advice
        </p>""", unsafe_allow_html=True)

        with st.container(border=True):
            choice_col, desc_col = st.columns([1, 2], gap="medium")
            with choice_col:
                uploaded_file = st.file_uploader("Choose CV/Resume", type=["pdf", "docx", "txt"], key="cv_file_uploader")
                if uploaded_file:
                    is_valid, message = validate_file(uploaded_file)
                    if not is_valid:
                        st.error(message)
                    else:
                        st.success("File validated!")
                        resume_text = extract_text_from_file(uploaded_file)
                        if resume_text:
                            st.session_state['resume_text'] = resume_text
                            
                selected_model_name = st.selectbox("Select AI Model",list(CV_INTERVIEW_MODELS.keys()), index=0, key="cv_model_select")
                selected_model = CV_INTERVIEW_MODELS[selected_model_name]
                temperature = st.slider("Temperature", 0.0, 1.0, 0.3, 0.1, key="cv_temperature")
                
            with desc_col:
                job_description = st.text_area("Paste job description", height=200, key="cv_job_description")

        # --- Helper to handle generation and session reset ---
        def handle_generation(prompt_text, session_title_prefix, response_header):
            if 'resume_text' not in st.session_state:
                st.error("Upload resume first!")
                return

            with st.spinner("Generating..."):
                try:
                    # 1. CREATE NEW SESSION
                    new_sess_id = create_chat_session(
                        user_id, 
                        tab_name, 
                        first_message=f"{session_title_prefix} for CV"
                    )
                    
                    # 2. UPDATE STATE & CLEAR HISTORY
                    st.session_state[session_id_key] = new_sess_id
                    st.session_state[messages_key] = []
                    
                    # 3. GENERATE CONTENT
                    llm = ChatGroq(model=selected_model, temperature=temperature, groq_api_key=os.getenv("GROQ_API_KEY"))
                    response = llm.invoke(prompt_text).content
                    
                    # 4. SAVE & DISPLAY
                    full_response = f"**{response_header}**\n\n{response}"
                    st.session_state[messages_key].append({"role": "assistant", "content": full_response})
                    save_chat_message(user_id, new_sess_id, tab_name, "assistant", full_response)
                    
                    st.success("Done!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")

        # --- Buttons ---
        blank1, intercol, skillcol, blank2 = st.columns([2,1,1,2])
        
        with intercol:
            if st.button("Interview Questions", key="cv_gen_questions"):
                prompt = f"""
ROLE: You are an expert technical recruiter and hiring manager. Your task is to generate highly targeted interview questions based strictly on the resume (and job description if available). Do NOT assume or invent experience not stated in the resume. If a question is based on inferred skills, label it as: (Assumed – verify with candidate).

INPUT:
RESUME:
{st.session_state['resume_text']}

{f'JOB DESCRIPTION:\n{job_description}' if job_description else ''}

OUTPUT REQUIREMENTS:
- Generate exactly 40 interview questions.
- Categorize them into:
    1. Behavioral (4-5 questions)
    2. Technical / Domain-Specific (25-30 questions) again sub-categorize into:
        - Different skill sets or domains as mentioned in the resume (e.g. Python, Six Sigma, Excel, SQL, etc.)
    3. Role Alignment & Career Fit (4-5 questions)
- Each question must be:
    - Clear, concise, and directly tied to the resume and job scope.
    - Written using strong employment and HR vocabulary (competencies, outcomes, ownership, metrics, scope, stakeholder alignment, delivery impact).
- For each question, include a short note in brackets indicating what the interviewer is assessing (e.g., "assessing analytical capability", "evaluating hands-on expertise", "testing ownership and accountability").

CONSTRAINTS:
- Do NOT invent skills or experience that do not appear in the resume.
- Avoid generic or filler questions — they must feel personalized and intentional.
- No hypothetical irrelevant scenarios unless directly tied to the role.

Return only the interview questions in the requested structured format.
"""

                
                handle_generation(prompt, "Interview Questions", "Generated Interview Questions:")
        
        with skillcol:
            if st.button("Skill Highlights", key="cv_skill_highlights"):
                prompt = f"""
ROLE: You are a professional career strategist, HR consultant, and hiring manager specializing in competency-based evaluation. Analyze the resume strictly based on the provided content. Do NOT infer or fabricate experiences not explicitly present.

INPUT:
RESUME:
{st.session_state['resume_text']}

OUTPUT FORMAT (follow strictly):

1. **Top 5 Most Evident and Marketable Skills**
   - For each skill:
        - Name of the skill
        - Evidence from resume (quote line or summarize)
        - Type of skill (Technical / Soft / Hybrid)
        - Real-world hiring value (1–2 sentences)

2. **How to Present Each Skill Effectively**
   - Provide clear, recruiter-level phrasing using achievement-driven and metrics-focused language (STAR or CAR style).
   - Include one example rewritten bullet point improvement for each skill.

3. **Questions to Prepare For**
   - 6–10 targeted questions hiring managers could ask to validate the listed skills.
   - Label questions by category: Technical Validation / Experience Depth / Behavioral Competency / Role Positioning.

4. **Skill Gaps to Address**
   - Identify possible missing or weak areas relevant to the resume content and (if strong signals exist) the likely role.
   - Provide:
        - Gap name
        - Why it matters in hiring evaluations
        - Suggested Learning or Upskilling Direction (tools, frameworks, certifications, expected capabilities)

CONSTRAINTS:
- Do not hallucinate certifications, job titles, or achievements.
- If information is missing or unclear, state: "Information insufficient — recommend adding clarity."
- Use recruitment-grade, direct, and actionable wording.

Return information in structured bullet points — no filler commentary.
"""
                
                
                handle_generation(prompt, "Skill Analysis", "Skill Highlights Analysis:")
        
        # --- Chat Interface ---
        st.markdown("---")
        st.markdown("""<h4 style='text-align: left; color: #33FF33;'>👨‍🏫 Chat with Career Coach</h4>""", unsafe_allow_html=True)
        
        # Display current session messages
        for msg in st.session_state[messages_key]:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
        
        if user_input := st.chat_input("Ask your coach...", key="cv_chat_input"):
            current_sess_id = st.session_state[session_id_key]
            
            # Update title if it's a generic "New Chat"
            update_session_title_if_new(current_sess_id, user_input)
            
            # User Message
            st.session_state[messages_key].append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.write(user_input)
            save_chat_message(user_id, current_sess_id, tab_name, "user", user_input)
            
            # Assistant Message
            with st.spinner("Coach is thinking..."):
                try:
                    llm = ChatGroq(model=selected_model, temperature=temperature, groq_api_key=os.getenv("GROQ_API_KEY"))
                    
                    context = f"""{SYSTEM_PROMPTS['cv_interview']}\nRESUME: {st.session_state.get('resume_text', 'Not provided')}\nJOB DESCRIPTION: {job_description if job_description else 'Not provided'}"""
                    
                    # Only include recent history to avoid token limits
                    history_tuples = [(m["role"], m["content"]) for m in st.session_state[messages_key][-10:]]
                    prompt = ChatPromptTemplate.from_messages([("system", context), *history_tuples])
                    
                    response = llm.invoke(prompt.format_prompt().to_messages()).content
                    
                    st.session_state[messages_key].append({"role": "assistant", "content": response})
                    with st.chat_message("assistant"):
                        st.write(response)
                        
                    save_chat_message(user_id, current_sess_id, tab_name, "assistant", response)
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")