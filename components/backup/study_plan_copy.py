"""
Study Plan Generator Tab
"""

import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from utils.chat_history import initialize_chat_history, add_message, display_chat_history, format_chat_history_for_llm
from config import STUDY_PLAN_MODELS, SYSTEM_PROMPTS, STUDY_MIN_WEEKS, STUDY_MAX_WEEKS
import os

def study_plan_tab():
    """Study Plan Generator Tab"""

    st.markdown("""
    <h4 style='text-align: left; color: #33FF33;'>
    📋🗓️ Ab toh padhle! 
    </h4>
    """,
    unsafe_allow_html=True)


    st.markdown("""
    <p style='text-align: left; color: #FF66B2;'>
       Create personalized study plans with week-by-week schedules,resources, and progress metrics
    </p>
    """, 
    unsafe_allow_html=True)
    
    # Initialize session state
    tab_key = "study_plan"
    initialize_chat_history(tab_key)
    
    # Sidebar Configuration
    # Study Plan Configuration

    with st.container(border=True):
        acol, bcol= st.columns([1,2])

        
        with acol:
            subject = st.text_input("Subject/Topic",placeholder="What to study?",key="study_subject")

            learning_goal = st.text_input("Learning Goal",placeholder="What to achieve?",key="study_goal")
        
        with bcol:
            lcol, rcol = st.columns([1,1])
            with lcol:
                knowledge_level = st.selectbox("Knowledge Level",["Beginner", "Intermediate", "Advanced"],key="study_level")

                learning_style = st.multiselect("Learning Methods",["Videos", "Books", "Practice", "Discussions", "Projects"],
                default=["Videos", "Practice"],key="study_style")

                
                selected_model_name = st.selectbox("Select AI Model",list(STUDY_PLAN_MODELS.keys()),
                index=list(STUDY_PLAN_MODELS.keys()).index("Groq Compound Mini (Best)"),key="study_model_select")
                selected_model = STUDY_PLAN_MODELS[selected_model_name]

                
            with rcol:
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
                    
                    prompt_text = f"""Create comprehensive study plan:

Subject: {subject}
Duration: {duration_weeks} weeks
Level: {knowledge_level}
Goal: {learning_goal}
Daily Hours: {daily_hours} hours
Methods: {', '.join(learning_style)}

Include:
1. Overview of what will be covered
2. Learning objectives
3. Week-by-week schedule with topics
4. Recommended resources
5. Progress tracking metrics
6. Success tips

Format clearly with proper headings."""
                    
                    response = llm.invoke(prompt_text)
                    study_plan = response.content
                    
                    st.session_state['generated_study_plan'] = study_plan
                    st.session_state['study_subject'] = subject
                    
                    add_message(tab_key, "assistant", f"**Study Plan for {subject}**\n\n{study_plan}")
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
        add_message(tab_key, "user", user_input)
        
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
                st.rerun()
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
