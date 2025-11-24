"""
Article Generator Tab
"""

import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from utils.file_handler import validate_file, extract_text_from_file
from utils.chat_history import initialize_chat_history, add_message, display_chat_history, get_chat_history, format_chat_history_for_llm
from utils.memory import save_chat_message, get_chat_history
from utils.chat_sessions import create_chat_session, get_user_sessions, get_session_messages, update_session_title_if_new
from components.chat_library import show_chat_library
from config import ARTICLE_GENERATOR_MODELS, SYSTEM_PROMPTS, WRITING_STYLES, ARTICLE_MAX_WORDS, ARTICLE_MIN_WORDS, ARTICLE_DEFAULT_WORDS
import os

def article_generator_tab():
    """Article Generator Tab"""

    user_id = st.session_state.user["id"]
    tab_name = "Article Generator"
    tab_key = "article_generator"

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
    show_chat_library(user_id, tab_name, tab_key, lib_col)

    with main_col:
        st.markdown("""
    <h4 style='text-align: left; color: #33FF33;'>
    📜✒️ Taarak Mehta here!
    </h4>
    """,
    unsafe_allow_html=True)


        st.markdown("""
    <p style='text-align: left; color: #FF66B2;'>
       Create well-researched articles with customizable settings for style
    </p>
    """, 
    unsafe_allow_html=True)
    # Article Configuration
        with st.container(border=True):
            topic_col, select_col, slider_col = st.columns([2,1,1])
            
            with topic_col:
                article_topic = st.text_input("Article Topic",placeholder="Enter article topic...",key="article_topic")
            sour_col, cont_col = st.columns(2)
            
            with sour_col:
                include_sources = st.checkbox("Include sources",value=True,key="article_sources")
                
            with cont_col:
                include_toc = st.checkbox("Include table of contents",value=True,key="article_toc")
                
            
            with select_col:
                writing_style = st.selectbox("Writing Style",WRITING_STYLES,key="article_style")
                selected_model_name = st.selectbox("Select AI Model",list(ARTICLE_GENERATOR_MODELS.keys()),
                            index=list(ARTICLE_GENERATOR_MODELS.keys()).index("Groq Compound (Best)"),key="article_model_select")
                selected_model = ARTICLE_GENERATOR_MODELS[selected_model_name]
                
                

            with slider_col:
                word_count = st.slider("Target Word Count",min_value=ARTICLE_MIN_WORDS, max_value=ARTICLE_MAX_WORDS,
                    value=ARTICLE_DEFAULT_WORDS,step=100,key="article_word_count")
                temperature = st.slider("Creativity Level",min_value=0.0,max_value=1.0,
                    value=0.3,step=0.1,key="article_temperature")
                

        # Additional Options
        with st.expander("⚠️🚫 Temperature Guidance ", expanded=False):
            st.markdown(
            """
            <h5 style='color:#b8860b;'>How to use the temperature setting for Article Generation:</h5>
            <span style='color:#b8860b;'>
            • <b>0.0–0.3: Highly factual, less creative.</b> Suitable for technical, academic, or reference-style articles.<br>
            • <b>0.4–0.7: Balanced creativity and accuracy.</b> Great for most blog posts, tutorials, or explainers.<br>
            • <b>0.8–1.0: Most creative,</b> ideal for stories or highly original content, but greater risk of hallucination.<br><br>
            <b>Tip:</b> For important topics, use 0.4–0.5. For brainstorming or creative styles, go higher!
            </span>
            """,
            unsafe_allow_html=True
        )

        
        
        # Generate Button
        if st.button("Generate Article", key="article_generate"):
            if not article_topic:
                st.error("Enter article topic!")
            else:
                with st.spinner("Generating article..."):
                    try:
                        llm = ChatGroq(
                            model=selected_model,
                            temperature=temperature,
                            groq_api_key=os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
                        )
                        prompt_text = f"""Write a comprehensive article on:

    Topic: {article_topic}
    Word Count: {word_count} words
    Style: {writing_style}
    Creativity: {temperature} (0=factual, 1=creative)
    {f'Include: References' if include_sources else 'No external references'}
    {f'Include: Table of contents' if include_toc else ''}

    Requirements:
    - Well-researched and accurate
    - Engaging and well-structured
    - Clear headings
    - Professional formatting
    - Publication-ready

    Write now:"""
                        response = llm.invoke(prompt_text)
                        article_content = response.content
                        st.session_state['generated_article'] = article_content
                        # REMOVE this line:
                        # st.session_state['article_topic'] = article_topic
                        
                        add_message(tab_key, "assistant", "Let's discuss more on the above article. What would you like to refine, expand, or ask about?")
                        st.success("Generated!")
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        # Display Generated Article
        if 'generated_article' in st.session_state:
            st.markdown("---")
            st.markdown("""
            <h4 style='text-align: left; color: #33FF33;'>
            ✅ Generated Article 
            </h4>
            """, 
            unsafe_allow_html=True)
            
            col1, col2 = st.columns([4, 1])
            with col1:
                # Just READ the value
                st.markdown(f"**Topic:** {article_topic}")
            
            st.markdown("---")
            st.markdown(st.session_state['generated_article'])
        
        # Chat Interface
        st.markdown("---")
        # st.markdown("#### Chat with Editor")
        st.markdown("""
        <h4 style='text-align: left; color: #33FF33;'>
        ✍🏻 Chat with Editor
        </h4>
        """,
        unsafe_allow_html=True)
        # st.markdown("Refine, expand, or modify sections!")
        
        display_chat_history(tab_key)
        
        user_input = st.chat_input(
            "Ask about article...",
            key="article_chat_input"
        )
        
        if user_input:
            session_id = st.session_state.current_session_id
            current_sess_id = st.session_state[session_id_key]
            update_session_title_if_new(current_sess_id, user_input)
            st.session_state[messages_key].append({"role": "user", "content": user_input})
            add_message(tab_key, "user", user_input)
            save_chat_message(user_id, current_sess_id, tab_name, "user", user_input)
            
            with st.spinner("Editor is working..."):
                try:
                    llm = ChatGroq(
                        model=selected_model,
                        temperature=temperature,
                        groq_api_key=os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
                    )
                    
                    context = f"""{SYSTEM_PROMPTS['article_generator']}

    Article being edited:
    {st.session_state.get('generated_article', 'Not yet generated')}"""
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

