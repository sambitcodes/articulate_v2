"""
Article Generator Tab
"""

import streamlit as st
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from utils.chat_history import initialize_chat_history, add_message, display_chat_history, format_chat_history_for_llm
from config import ARTICLE_GENERATOR_MODELS, SYSTEM_PROMPTS, WRITING_STYLES, ARTICLE_MAX_WORDS, ARTICLE_MIN_WORDS, ARTICLE_DEFAULT_WORDS
import os

def article_generator_tab():
    """Article Generator Tab"""
    
    st.markdown("### 📝 Article Generator")
    st.markdown(
        "Create well-researched articles with customizable settings for style, "
        "length, and creativity level."
    )
    
    # Initialize session state
    tab_key = "article_generator"
    initialize_chat_history(tab_key)
    
    # Sidebar Configuration
    with st.sidebar:
        st.markdown("#### Settings - Article Generator")
        selected_model_name = st.selectbox(
            "Select AI Model",
            list(ARTICLE_GENERATOR_MODELS.keys()),
            index=list(ARTICLE_GENERATOR_MODELS.keys()).index("Groq Compound (Default)"),
            key="article_model_select"
        )
        selected_model = ARTICLE_GENERATOR_MODELS[selected_model_name]
        
        temperature = st.slider(
            "Creativity Level",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            key="article_temperature"
        )
    
    # Article Configuration
    col1, col2, col3 = st.columns(3)
    
    with col1:
        article_topic = st.text_input(
            "Article Topic",
            placeholder="Enter article topic...",
            key="article_topic"
        )
    
    with col2:
        word_count = st.slider(
            "Target Word Count",
            min_value=ARTICLE_MIN_WORDS,
            max_value=ARTICLE_MAX_WORDS,
            value=ARTICLE_DEFAULT_WORDS,
            step=100,
            key="article_word_count"
        )
    
    with col3:
        writing_style = st.selectbox(
            "Writing Style",
            WRITING_STYLES,
            key="article_style"
        )
    
    # Additional Options
    col1, col2 = st.columns(2)
    
    with col1:
        include_sources = st.checkbox(
            "Include sources",
            value=True,
            key="article_sources"
        )
    
    with col2:
        include_toc = st.checkbox(
            "Include table of contents",
            value=True,
            key="article_toc"
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
        st.markdown("#### Generated Article")
        
        col1, col2 = st.columns([4, 1])
        with col1:
            # Just READ the value
            st.markdown(f"**Topic:** {article_topic}")
        
        st.markdown("---")
        st.markdown(st.session_state['generated_article'])
    
    # Chat Interface
    st.markdown("---")
    st.markdown("#### Chat with Editor")
    st.markdown("Refine, expand, or modify sections!")
    
    display_chat_history(tab_key)
    
    user_input = st.chat_input(
        "Ask about article...",
        key="article_chat_input"
    )
    
    if user_input:
        add_message(tab_key, "user", user_input)
        
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
                st.rerun()
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
