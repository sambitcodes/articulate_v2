"""
Study Plan Generator Tab
"""

import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from utils.file_handler import validate_file, extract_text_from_file
from utils.chat_history import initialize_chat_history, add_message, display_chat_history, get_chat_history, format_chat_history_for_llm
from utils.memory import save_chat_message, get_chat_history
from utils.chat_sessions import create_chat_session, get_user_sessions, get_session_messages, update_session_title_if_new
from components.chat_library import show_chat_library
from config import STUDY_PLAN_MODELS, SYSTEM_PROMPTS, STUDY_MIN_WEEKS, STUDY_MAX_WEEKS
import os

def study_plan_tab():
    """Study Plan Generator Tab"""
    
    user_id = st.session_state.user["id"]
    tab_name = "Study Plan"
    tab_key = "study_plan"
    
    # Initialize session state
    session_id_key = f"session_id_{tab_key}"
    messages_key = f"messages_{tab_key}"

    if session_id_key not in st.session_state:
        # Check DB for recent session
        sessions = get_user_sessions(user_id, tab_name, limit=1)
        if sessions:
            # Resume latest
            latest_session = sessions[0]
            st.session_state[session_id_key] = latest_session[0]
            db_msgs = get_session_messages(latest_session[0])
            st.session_state[messages_key] = [{"role": r, "content": c} for r, c, _ in db_msgs]
        else:
            # Create fresh
            new_id = create_chat_session(user_id, tab_name)
            st.session_state[session_id_key] = new_id
            st.session_state[messages_key] = []
            
    # Ensure messages list exists
    if messages_key not in st.session_state:
        st.session_state[messages_key] = []
    
    main_col, lib_col = st.columns([4, 1])
    show_chat_library(user_id, tab_name, tab_key, lib_col)   # Sidebar Configuration
    # Study Plan Configuration

    with main_col:
        
        st.markdown("""<h4 style='text-align: left; color: #33FF33;'>📋🗓️ Ab toh padhle! </h4>""",unsafe_allow_html=True)
        st.markdown("""<p style='text-align: left; color: #FF66B2;'>
       Create personalized study plans with week-by-week schedules,resources, and progress metrics</p>""", unsafe_allow_html=True)
    
        with st.container(border=True):
            acol, bcol, ccol= st.columns([1,1,1])

            
            with acol:
                subject = st.text_input("Subject/Topic",placeholder="What to study?",key="study_subject")

                learning_goal = st.text_input("Learning Goal",placeholder="What to achieve?",key="study_goal")
            
            with bcol:
                    knowledge_level = st.selectbox("Knowledge Level",["Beginner", "Intermediate", "Advanced"],key="study_level")

                    learning_style = st.multiselect("Learning Methods",["Videos", "Books", "Practice", "Discussions", "Projects"],
                    default=["Videos", "Practice"],key="study_style")

                    selected_model_name = st.selectbox("Select AI Model",list(STUDY_PLAN_MODELS.keys()),
                    index=list(STUDY_PLAN_MODELS.keys()).index("Groq Compound Mini (Best)"),key="study_model_select")
                    selected_model = STUDY_PLAN_MODELS[selected_model_name]

                    
            with ccol:
                    duration_weeks = st.slider("Duration (Weeks)",min_value=STUDY_MIN_WEEKS,max_value=STUDY_MAX_WEEKS,
                    value=4,key="study_duration")

                    daily_hours = st.slider("Daily Study Hours",min_value=0.5,max_value=8.0,
                    value=2.0,step=0.5,key="study_daily_hours")

                    temperature = st.slider("Temperature",min_value=0.0,max_value=1.0,
                    value=0.2,step=0.1,key="study_temperature")

        with st.expander("⚠️🚫 Temperature Guidance ", expanded=False):
            st.markdown(
            """
            <h5 style='color:#b8860b;'>How to use the temperature setting for Study Plans:</h5>
            <span style='color:#b8860b;'>
            • <b>0.0–0.3: Realistic and focused.</b> Gives structured, truly actionable plans.<br>
            • <b>0.4–0.7: Adds variety and more creative ideas.</b> Good for motivation tips and unique resource suggestions.<br>
            • <b>0.8–1.0: Highly creative,</b> may include unconventional or less practical suggestions.<br><br>
            <b>Tip:</b> Lower settings are best if you want reliable timelines; use higher only if you want a more “innovative” plan!
            </span>
            """,
            unsafe_allow_html=True
        )

            
            
        # Generate Plan Button
        if st.button("Generate Study Plan", key="study_generate"):
            if not subject:
                st.error("Enter a subject!")
            else:
                with st.spinner("Creating study plan..."):
                    try:
                        llm = ChatGroq(
                            model=selected_model,
                            temperature=temperature,
                            groq_api_key=os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
                        )
                        
                        prompt_text = f"""
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

                        
                        response = llm.invoke(prompt_text)
                        study_plan = response.content
                        
                        st.session_state['generated_study_plan'] = study_plan
                        st.session_state['study_subject'] = subject
                        
                        add_message(tab_key, "assistant", f"**Study Plan for {subject}**\n\n{study_plan}")
                        
                        if f"cached_sessions_list_{tab_key}" in st.session_state:
                            del st.session_state[f"cached_sessions_list_{tab_key}"]
                        
                        st.success("Plan created!")
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        # Display Generated Plan
        if 'generated_study_plan' in st.session_state:
            st.markdown("---")
            st.markdown("#### Your Study Plan")
            
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**Subject:** {st.session_state.get('study_subject', 'N/A')}")
            
            st.markdown("---")
            st.markdown(st.session_state['generated_study_plan'])
        
        # Chat Interface
        st.markdown("---")
        # st.markdown("#### Chat with Study Mentor")
        
        st.markdown("""
        <h4 style='text-align: left; color: #33FF33;'>
        🤝 Chat with Study Mentor
        </h4>
        """,
        unsafe_allow_html=True)
        
        # st.markdown("Customize the plan or get recommendations!")
        
        display_chat_history(tab_key)
        
        user_input = st.chat_input(
            "Ask mentor...",
            key="study_chat_input"
        )
        
        if user_input:
            session_id = st.session_state.current_session_id
            current_sess_id = st.session_state[session_id_key]
            update_session_title_if_new(current_sess_id, user_input)
            st.session_state[messages_key].append({"role": "user", "content": user_input})
            add_message(tab_key, "user", user_input)
            save_chat_message(user_id, current_sess_id,tab_name, "user", user_input)
            
            with st.spinner("Mentor preparing response..."):
                try:
                    llm = ChatGroq(
                        model=selected_model,
                        temperature=temperature,
                        groq_api_key=os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
                    )
                    
                    context = f"""{SYSTEM_PROMPTS['study_plan']}

    Study Plan:
    {st.session_state.get('generated_study_plan', 'Not yet generated')}"""
                    
                    chat_history = format_chat_history_for_llm(tab_key)
                    
                    prompt = ChatPromptTemplate.from_messages([
                        ("system", context),
                        *[(msg["role"], msg["content"]) for msg in chat_history]
                    ])
                    
                    response = llm.invoke(prompt.format_prompt().to_messages())
                    assistant_response = response.content
                    
                    add_message(tab_key, "assistant", assistant_response)
                    st.session_state[messages_key].append({"role": "assistant", "content": assistant_response})
                    save_chat_message(user_id, current_sess_id, tab_name, "assistant", assistant_response)
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
