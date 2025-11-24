"""
Article Generator Tab - Updated for Session Isolation
"""

import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from utils.memory import save_chat_message
# Import create_chat_session to allow making new sessions on demand
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
    
    # --- Initialization Logic ---
    # This loads the last session ONLY if we don't have one active.
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

    # --- UI Layout ---
    main_col, lib_col = st.columns([4, 1])
    
    # 1. Show the Chat Library (Sidebar history)
    show_chat_library(user_id, tab_name, tab_key, lib_col)

    with main_col:
        st.markdown("""<h4 style='text-align: left; color: #33FF33;'>📜✒️ Taarak Mehta here!</h4>""", unsafe_allow_html=True)
        st.markdown("""<p style='text-align: left; color: #FF66B2;'>Create well-researched articles with customizable settings for style</p>""", unsafe_allow_html=True)
        
        # Inputs
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

        # --- GENERATION LOGIC (CRITICAL FIX) ---
        if st.button("Generate Article", key="article_generate"):
            if not article_topic:
                st.error("Enter article topic!")
            else:
                with st.spinner("Generating article..."):
                    try:
                        # 1. FORCE NEW SESSION [FIX]
                        # Instead of using the old session, we create a fresh one immediately.
                        # We use the topic as the "first message" implicitly for the title.
                        new_sess_id = create_chat_session(user_id, tab_name, first_message=f"Article: {article_topic}")
                        
                        # 2. UPDATE STATE [FIX]
                        # Point the app to this new session ID
                        st.session_state[session_id_key] = new_sess_id
                        
                        # 3. CLEAR HISTORY [FIX]
                        # Wipe the UI chat messages clean
                        st.session_state[messages_key] = []
                        
                        # Generate content
                        llm = ChatGroq(model=selected_model, temperature=temperature, groq_api_key=os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY"))
                        prompt_text = f"""You are an expert researcher and professional writer.

Your task is to generate a high-quality, publication-ready article with the following specifications:

Topic: **{article_topic}**  
Target Word Count: **{word_count} words**  
Writing Style: **{writing_style}**  
Creativity Level: **{temperature}** (0 = factual/technical, 1 = highly creative)  
{f'Include a properly formatted "Table of Contents" section at the beginning.' if include_toc else ''}
{f'Include reliable external references and citations formatted consistently (APA/MLA/Harvard — choose one and follow it throughout).' if include_sources else 'Do not include external references.'}

---

### **Content Requirements**

- The article must be **deeply researched**, logically structured, and written with **high linguistic precision**.
- Use clear **H1, H2, H3 headings**, and avoid overly long paragraphs.
- Maintain a tone suitable for publication (academic, journalistic, editorial, or as per the style defined).
- Include:
  - Definitions and explanations where needed  
  - Examples, case studies, or real-world applications (when relevant)  
  - Statistics, evidence, or insights (only if accurate and verifiable — no fabricated facts)
- Ensure the narrative flows smoothly using **cohesive transitions and varied sentence structure.**

---

### **Writing & Quality Standards**

- Vocabulary should be **rich, sophisticated, and contextually precise**, but avoid unnecessary jargon.
- Maintain clarity and readability — aim for a balance of accessibility and intellectual depth.
- Avoid repetition, filler content, generic phrasing, or vague statements.
- Ensure each section meaningfully contributes to the topic.
- Finish with a strong, concise conclusion that summarizes key insights and leaves the reader with takeaway value.

---

### **Output Format**

1. Begin writing immediately.
2. Do not show instructions or meta commentary.
3. Only output the final article, formatted cleanly.

----

Now, write the full article.:"""       
                        response = llm.invoke(prompt_text).content
                        st.session_state['generated_article'] = response
                        
                        # 4. SAVE TO NEW SESSION [FIX]
                        # Save this generated article as the *first* message in the NEW history
                        msg = f"**Generated Article for: {article_topic}**\n\n{response}"
                        
                        # Update UI state with just this one message
                        st.session_state[messages_key].append({"role": "assistant", "content": msg})
                        
                        # Save to Database using the NEW ID
                        save_chat_message(user_id, new_sess_id, tab_name, "assistant", msg)
                        
                        st.success("Generated!")
                        # Rerun to refresh the Chat Library list on the right immediately
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        # Display Generated Article (Current View)
        if 'generated_article' in st.session_state:
            st.markdown("---")
            st.markdown("""<h4 style='text-align: left; color: #33FF33;'>✅ Generated Article</h4>""", unsafe_allow_html=True)
            st.markdown(f"**Topic:** {article_topic}")
            st.markdown("---")
            st.markdown(st.session_state['generated_article'])
        
        # --- CHAT INTERFACE ---
        st.markdown("---")
        st.markdown("""<h4 style='text-align: left; color: #33FF33;'>✍🏻 Chat with Editor</h4>""", unsafe_allow_html=True)
        
        # Display History (Now isolated to the specific session)
        # for msg in st.session_state[messages_key]:
            # with st.chat_message(msg["role"]):
            #     st.write(msg["content"])
        
        user_input = st.chat_input("Ask about article...", key="article_chat_input")
        
        if user_input:
            current_sess_id = st.session_state[session_id_key]
            
            # Standard chat loop
            update_session_title_if_new(current_sess_id, user_input)
            st.session_state[messages_key].append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.write(user_input)
            
            save_chat_message(user_id, current_sess_id, tab_name, "user", user_input)
            
            with st.spinner("Editor is working..."):
                try:
                    llm = ChatGroq(model=selected_model, temperature=temperature, groq_api_key=os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY"))
                    context = f"{SYSTEM_PROMPTS['article_generator']}\nArticle being edited:\n{st.session_state.get('generated_article', 'Not yet generated')}"
                    
                    chat_history_llm = [(m["role"], m["content"]) for m in st.session_state[messages_key]]
                    prompt = ChatPromptTemplate.from_messages([("system", context), *chat_history_llm])
                    response = llm.invoke(prompt.format_prompt().to_messages()).content
                    
                    st.session_state[messages_key].append({"role": "assistant", "content": response})
                    with st.chat_message("assistant"):
                        st.write(response)
                    
                    save_chat_message(user_id, current_sess_id, tab_name, "assistant", response)
                    # No rerun needed here usually, but if you want to be safe:
                    # st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")