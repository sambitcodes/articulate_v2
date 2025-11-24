"""
Study Plan Generator Tab
"""

import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from utils.memory import save_chat_message
from utils.chat_sessions import create_chat_session, get_user_sessions, get_session_messages, update_session_title_if_new
from components.chat_library import show_chat_library
from config import STUDY_PLAN_MODELS, SYSTEM_PROMPTS, STUDY_MIN_WEEKS, STUDY_MAX_WEEKS
import os

def study_plan_tab():
    """Study Plan Generator Tab"""
    
    user_id = st.session_state.user["id"]
    tab_name = "Study Plan"
    tab_key = "study_plan"
    
    session_id_key = f"session_id_{tab_key}"
    messages_key = f"messages_{tab_key}"

    # --- Init ---
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
    

    main_col, lib_col = st.columns([4, 1])
    show_chat_library(user_id, tab_name, tab_key, lib_col)

    with main_col:
        st.markdown("""<h4 style='text-align: left; color: #33FF33;'>📋🗓️ Ab toh padhle! </h4>""",unsafe_allow_html=True)
        st.markdown("""<p style='text-align: left; color: #FF66B2;'>Create personalized study plans with week-by-week schedules</p>""", unsafe_allow_html=True)
    
        with st.container(border=True):
            acol, bcol, ccol= st.columns([1,1,1])
            with acol:
                subject = st.text_input("Subject/Topic", key="study_subject")
                learning_goal = st.text_input("Learning Goal", key="study_goal")
            with bcol:
                knowledge_level = st.selectbox("Knowledge Level",["Beginner", "Intermediate", "Advanced"],key="study_level")
                learning_style = st.multiselect("Methods",["Videos", "Books", "Practice"],default=["Videos"],key="study_style")
                selected_model_name = st.selectbox("Model",list(STUDY_PLAN_MODELS.keys()), index=0, key="study_model_select")
                selected_model = STUDY_PLAN_MODELS[selected_model_name]
            with ccol:
                duration_weeks = st.slider("Weeks", STUDY_MIN_WEEKS, STUDY_MAX_WEEKS, 4, key="study_duration")
                daily_hours = st.slider("Hours/Day", 0.5, 8.0, 2.0, 0.5, key="study_daily_hours")
                temperature = st.slider("Temp", 0.0, 1.0, 0.2, 0.1, key="study_temperature")

        # --- Generate Button ---
        if st.button("Generate Study Plan", key="study_generate"):
            if not subject:
                st.error("Enter a subject!")
            else:
                with st.spinner("Creating plan..."):
                    try:
                        
                        new_sess_id = create_chat_session(user_id, tab_name, first_message=f"Plan: {subject}")
                        st.session_state[session_id_key] = new_sess_id
                        st.session_state[messages_key] = []

                        prompt = f"""
ROLE: You are an expert curriculum designer and learning strategist. Your task is to create a precise, research-backed study plan based strictly on the given inputs. Do NOT add topics, skills, or timelines not supported by the inputs. If a detail is unclear or unspecified, state it neutrally rather than guessing.

INPUTS:
- Subject: {subject}
- Duration: {duration_weeks} weeks
- Current Knowledge Level: {knowledge_level}
- Learning Goal: {learning_goal}
- Daily Study Time: {daily_hours} hours/day
- Preferred Learning Methods: {', '.join(learning_style)}

OUTPUT STRUCTURE (follow exactly):

1. **Program Overview**
   - 4–7 sentence summary describing: scope of learning, alignment with input goal, expected difficulty, and learning strategy approach.

2. **Learning Objectives**
   - 6–10 clear, measurable, outcome-focused objectives using high-clarity verbs (e.g., analyze, apply, evaluate, implement, demonstrate).

3. **Week-by-Week Roadmap**
   - For each week:
       - Week number
       - Primary theme or milestone
       - Specific subtopics or modules
       - Expected outcome/end-of-week competency
       - Daily structure example based on provided daily hours and learning methods

   Requirements:
   - Timeline MUST stay aligned with the exact number of weeks and must not shift or condense content.
   - Maintain realistic pacing based on the learner’s level and hours/day.

4. **Recommended Resources**
   - Organize by type: Books/Textbooks, Videos/Courses, Tools/Software, Practice Platforms.
   - Only recommend widely available, reputable sources (avoid obscure or unverifiable ones).
   - If a resource may require payment, label it as: (Paid).

5. **Progress and Performance Metrics**
   - Define measurable checkpoints, reflection prompts, assignments, or benchmarks for each phase of the plan.
   - Include frequency of assessment (ex: weekly quiz, monthly project, spaced recall checkpoints).

6. **Success and Retention Strategies**
   - Provide actionable study techniques aligned to the learner’s stated methods.
   - Include motivation, time management, revision cycles, spaced repetition, and consistency guidelines.

CONSTRAINTS:
- Do NOT hallucinate niche tools, fake books, or fictional methodologies.
- Keep tone structured, professional, timeline-focused and easy for a learner to follow.
- Ensure clarity of format, proper headings, clean spacing, and logically sequenced instructional design.

Return ONLY the formatted study plan with no extra commentary.
"""
                        
                        llm = ChatGroq(model=selected_model, temperature=temperature, groq_api_key=os.getenv("GROQ_API_KEY"))
                        response = llm.invoke(prompt).content
                        # st.session_state['generated_study_plan'] = response
                        
                        msg = f"**Study Plan for {subject}**\n\n{response}"
                        st.session_state[messages_key].append({"role": "assistant", "content": msg})
                        save_chat_message(user_id, new_sess_id, tab_name, "assistant", msg)

                        if f"cached_sessions_list_{tab_key}" in st.session_state:
                            del st.session_state[f"cached_sessions_list_{tab_key}"]
                        
                        st.success("Created!")
                        st.rerun()

                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        # --- Chat Interface ---
        st.markdown("---")
        st.markdown("""<h4 style='text-align: left; color: #33FF33;'>🤝 Chat with Study Mentor</h4>""", unsafe_allow_html=True)
        
        for msg in st.session_state[messages_key]:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
        
        if user_input := st.chat_input("Ask mentor...", key="study_chat_input"):

            current_sess_id = st.session_state[session_id_key]
            update_session_title_if_new(current_sess_id, user_input)
            st.session_state[messages_key].append({"role": "user", "content": user_input})

            with st.chat_message("user"):
                st.write(user_input)

            save_chat_message(user_id, current_sess_id, tab_name, "user", user_input)
            
            with st.spinner("Thinking..."):
                try:
                    llm = ChatGroq(model=selected_model, temperature=temperature, groq_api_key=os.getenv("GROQ_API_KEY"))
                    context = f"{SYSTEM_PROMPTS['study_plan']}\nPlan Context:\n{st.session_state.get('generated_study_plan', 'None')}"
                    
                    hist = [(m["role"], m["content"]) for m in st.session_state[messages_key][-10:]]
                    prompt = ChatPromptTemplate.from_messages([("system", context), *hist])
                    response = llm.invoke(prompt.format_prompt().to_messages()).content
                    
                    st.session_state[messages_key].append({"role": "assistant", "content": response})
                    with st.chat_message("assistant"):
                        st.write(response)
                    
                    save_chat_message(user_id, current_sess_id, tab_name, "assistant", response)

                except Exception as e:
                    st.error(str(e))