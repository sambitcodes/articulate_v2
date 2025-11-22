"""
Code Explainer & Problem Solver Tab
"""

import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from utils.chat_history import initialize_chat_history, add_message, display_chat_history, format_chat_history_for_llm
from utils.memory import save_chat_message, get_chat_history
from config import CODE_EXPLAINER_MODELS, DEFAULT_CODE_MODEL, SYSTEM_PROMPTS
import os

def code_explainer_tab():
    """Code Explainer & Problem Solver Tab"""

    user_id = st.session_state.user["id"]
    tab_name = "Code Explainer"
    
    st.markdown("""
    <h4 style='text-align: left; color: #33FF33;'>
    👨‍💻⚛ Hacker hai bhai hacker!
    </h4>
    """,
    unsafe_allow_html=True)


    st.markdown("""
    <p style='text-align: left; color: #FF66B2;'>
       Paste your code for line-by-line explanations, error detection, Optimization suggestions, and problem solutions.
    </p>
    """, 
    unsafe_allow_html=True)
    
    
    # Initialize session state
    tab_key = "code_explainer"
    initialize_chat_history(tab_key)

    func_col, chat_col = st.columns([4,1])
    with func_col:          
        
    # Code Input
        with st.container(border=True):
            code_col, set_col = st.columns([8,2])
            with code_col:
                # st.markdown("#### Code Input")
                code_input = st.text_area(
                    "Paste your code",
                    height=300,
                    key="code_input",
                    placeholder="Paste Python, JavaScript, Java, or any code here..."
                )
            
                if code_input:
                    st.session_state['current_code'] = code_input
            
            with set_col:
                selected_model_name = st.selectbox("Select AI Model",list(CODE_EXPLAINER_MODELS.keys()),
                index=list(CODE_EXPLAINER_MODELS.keys()).index("Groq Compound (Best)"), key="code_model_select")
                selected_model = CODE_EXPLAINER_MODELS[selected_model_name]
                temperature = st.slider("Temperature",min_value=0.0,max_value=1.0,
                    value=0.2,step=0.1, key="code_temperature")

        with st.expander("⚠️🚫 Temperature Guidance", expanded=False):
            st.markdown(
                """
                <h5 style='color:#b8860b;'>How to use the temperature setting for Code Explanations:</h5>
                <span style='color:#b8860b;'>
                • <b>0.0–0.3: Strictly technical and deterministic.</b> Use for precise code walkthroughs and debugging.<br>
                • <b>0.4–0.7: Balanced explanations and suggestions.</b> Good for optimization tips and beginner-friendly output.<br>
                • <b>0.8–1.0: Creative,</b> but may result in speculative or non-standard solutions.<br><br>
                <b>Tip:</b> Prefer lower or mid temperatures for best error detection and line-by-line reasoning.
                </span>
                """,
                unsafe_allow_html=True
            )

        # Action Buttons
        exp_col, debug_col, opt_col = st.columns(3)
        
        with exp_col:
            if st.button("Explain Code", key="code_explain"):
                if 'current_code' not in st.session_state or not st.session_state['current_code']:
                    st.error("Paste code first!")
                else:
                    with st.spinner("Analyzing..."):
                        try:
                            llm = ChatGroq(
                                model=selected_model,
                                temperature=temperature,
                                groq_api_key=os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
                            )
                            
                            prompt_text = f"""Provide detailed line-by-line explanation of this code.

    CODE:
    ```
    {st.session_state['current_code']}
    ```

    Explain what each part does and why it's written that way."""
                            
                            response = llm.invoke(prompt_text)
                            explanation = response.content
                            
                            add_message(tab_key, "assistant", f"**Code Explanation:**\n\n{explanation}")
                            st.success("Ready!")
                            
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
        
        with debug_col:
            if st.button("Find Errors", key="code_debug"):
                if 'current_code' not in st.session_state or not st.session_state['current_code']:
                    st.error("Paste code first!")
                else:
                    with st.spinner("Debugging..."):
                        try:
                            llm = ChatGroq(
                                model=selected_model,
                                temperature=temperature,
                                groq_api_key=os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
                            )
                            
                            prompt_text = f"""Find errors and issues in this code:

    CODE:
    ```
    {st.session_state['current_code']}
    ```

    For each issue: identify it, explain why, provide fix, explain the fix."""
                            
                            response = llm.invoke(prompt_text)
                            debug_info = response.content
                            
                            add_message(tab_key, "assistant", f"**Error Analysis:**\n\n{debug_info}")
                            st.success("Done!")
                            
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
        
        with opt_col:
            if st.button("Optimize", key="code_optimize"):
                if 'current_code' not in st.session_state or not st.session_state['current_code']:
                    st.error("Paste code first!")
                else:
                    with st.spinner("Optimizing..."):
                        try:
                            llm = ChatGroq(
                                model=selected_model,
                                temperature=temperature,
                                groq_api_key=os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
                            )
                            
                            prompt_text = f"""Provide optimization suggestions for this code:

    CODE:
    ```
    {st.session_state['current_code']}
    ```

    Consider: time complexity, space complexity, readability, best practices."""
                            
                            response = llm.invoke(prompt_text)
                            optimizations = response.content
                            
                            add_message(tab_key, "assistant", f"**Optimizations:**\n\n{optimizations}")
                            st.success("Done!")
                            
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
        
        # Chat Interface
        st.markdown("---")
        # st.markdown("#### 🎓 Chat with Code Expert")
        st.markdown("""
        <h4 style='text-align: left; color: #33FF33;'>
        🎓 Chat with Code Expert
        </h4>
        """,
        unsafe_allow_html=True)
        
        display_chat_history(tab_key)
        
        user_input = st.chat_input(
            "Ask about code...",
            key="code_chat_input"
        )
        
        if user_input:
            add_message(tab_key, "user", user_input)
            save_chat_message(user_id, tab_name, "user", user_input)
            
            with st.spinner("Expert is analyzing..."):
                try:
                    llm = ChatGroq(
                        model=selected_model,
                        temperature=temperature,
                        groq_api_key=os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
                    )
                    
                    context = f"""{SYSTEM_PROMPTS['code_explainer']}

    Current code:
    ```
    {st.session_state.get('current_code', 'Not provided')}
    ```"""
                    
                    chat_history = format_chat_history_for_llm(tab_key)
                    
                    prompt = ChatPromptTemplate.from_messages([
                        ("system", context),
                        *[(msg["role"], msg["content"]) for msg in chat_history]
                    ])
                    
                    response = llm.invoke(prompt.format_prompt().to_messages())
                    assistant_response = response.content
                    
                    add_message(tab_key, "assistant", assistant_response)
                    save_chat_message(user_id, tab_name, "assistant", assistant_response)
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    with chat_col:
        if st.button("📜 View Chat History", key="code_chat_history"):
            history = get_chat_history(user_id, tab_name)
            for role, content, timestamp in history:
                st.markdown(f"**{role}:** {content[:100]}...")
                st.markdown(f"*Timestamp: {timestamp}*")
