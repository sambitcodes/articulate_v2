"""
Code Explainer & Problem Solver Tab
"""

import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from utils.memory import save_chat_message
from utils.chat_sessions import create_chat_session, get_user_sessions, get_session_messages, update_session_title_if_new
from components.chat_library import show_chat_library
from config import CODE_EXPLAINER_MODELS, SYSTEM_PROMPTS
import os

def code_explainer_tab():
    """Code Explainer & Problem Solver Tab"""

    user_id = st.session_state.user["id"]
    tab_name = "Code Explainer"
    tab_key = "code_explainer"

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

    # --- Layout ---
    main_col, lib_col = st.columns([4, 1])
    show_chat_library(user_id, tab_name, tab_key, lib_col)
      
    with main_col:  
        st.markdown("""<h4 style='text-align: left; color: #33FF33;'>👨‍💻 Hacker hai bhai hacker!</h4>""", unsafe_allow_html=True)
        st.markdown("""<p style='text-align: left; color: #FF66B2;'>Paste your code for line-by-line explanations, error detection, and optimization.</p>""", unsafe_allow_html=True)        
        
        with st.container(border=True):
            code_col, set_col = st.columns([8,2])
            with code_col:
                code_input = st.text_area("Paste your code", height=300, key="code_input", placeholder="Paste Python, JavaScript, Java, or any code here...")
                if code_input:
                    st.session_state['current_code'] = code_input
            
            with set_col:
                selected_model_name = st.selectbox("Select AI Model",list(CODE_EXPLAINER_MODELS.keys()), index=0, key="code_model_select")
                selected_model = CODE_EXPLAINER_MODELS[selected_model_name]
                temperature = st.slider("Temperature", 0.0, 1.0, 0.2, 0.1, key="code_temperature")

        with st.expander("⚠️🚫 Temperature Guidance", expanded=False):
            st.markdown("""<h5 style='color:#b8860b;'>How to use the temperature setting:</h5>...""", unsafe_allow_html=True)

        # --- Helper for Action Buttons ---
        def run_code_action(prompt_text, session_prefix, output_header):
            if 'current_code' not in st.session_state or not st.session_state['current_code']:
                st.error("Paste code first!")
                return
            
            with st.spinner("Analyzing..."):
                try:
                    # 1. Create New Session
                    code_snippet = st.session_state['current_code'][:30].replace("\n", " ")
                    new_sess_id = create_chat_session(user_id, tab_name, first_message=f"{session_prefix}: {code_snippet}")
                    
                    # 2. Reset State
                    st.session_state[session_id_key] = new_sess_id
                    st.session_state[messages_key] = []
                    
                    # 3. Generate
                    llm = ChatGroq(model=selected_model, temperature=temperature, groq_api_key=os.getenv("GROQ_API_KEY"))
                    response = llm.invoke(prompt_text).content
                    
                    # 4. Save
                    full_msg = f"**{output_header}**\n\n{response}"
                    st.session_state[messages_key].append({"role": "assistant", "content": full_msg})
                    save_chat_message(user_id, new_sess_id, tab_name, "assistant", full_msg)
                    
                    if f"cached_sessions_list_{tab_key}" in st.session_state:
                        del st.session_state[f"cached_sessions_list_{tab_key}"]
                    
                    st.success("Done!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")

        exp_col, debug_col, opt_col = st.columns(3)
        
        with exp_col:
            if st.button("Explain Code", key="code_explain"):
                prompt = f"""INSTRUCTION: You are a careful, expert programmer and teacher. Detect the language automatically (or say which language you assumed). Read the CODE below and produce a thorough, line-by-line explanation that is precise, factual, and avoids speculation.

    CODE:
    ```
    {st.session_state['current_code']}
    ```    
        REQUIREMENTS & OUTPUT FORMAT:
        1. Start with a one-paragraph summary (2–3 sentences) that states the language, overall purpose of the snippet, and high-level behaviour.
        2. Then provide a numbered, line-by-line breakdown. For each line (or small group of closely related lines) include:
        - the exact line number(s) and the original code (preserve indentation),
        - a concise plain-English explanation of *what* it does,
        - why it is written that way (design intent / common idioms),
        - important side effects (state changes, I/O, exceptions it may raise),
        - any implicit assumptions (e.g., types, variable shapes, global state).
        3. After the line-by-line section, include:
        - a "Key variables & data structures" section that lists each important variable, its type/shape, and meaning,
        - a "Control flow summary" that explains loops, branches, and sequence of execution,
        - a "Potential pitfalls & gotchas" list (runtime errors, threading issues, security concerns, edge cases) with concrete examples.
        4. Finish with a "Suggested next steps" section: 3–6 short, pragmatic actions (tests to add, assertions, logging, input validation) to increase safety and correctness.

        CONSTRAINTS:
        - Do not invent behavior not present in the code. If a value/type is ambiguous, state the ambiguity explicitly and the reasonable assumptions you made.
        - Use clear, technical language and code vocabulary (e.g., "mutable", "side effect", "O(n)" if relevant).
        - Keep each line explanation to 1–4 sentences.

        Return only the structured text described above (no extra preamble).
        """

                run_code_action(prompt, "Explain Code", "Code Explanation")
        
        with debug_col:
            if st.button("Find Errors", key="code_debug"):
                prompt = f"""INSTRUCTION: You are an expert code reviewer and debugger. Read the CODE below and find *all* issues: bugs, logic errors, style problems, security issues, resource leaks, concurrency problems, and potential performance pitfalls. For each issue, provide a clear explanation and a minimal, correct fix. If you change behavior, explain tradeoffs.

    CODE:
    ```
    {st.session_state['current_code']}
    ```  
        REQUIREMENTS & OUTPUT FORMAT:
        1. Top summary: one short paragraph that states language, whether the code runs as-is, and an overall severity rating (e.g., "Safe to run", "Needs fixes before running", "Unsafe — keeps secrets/executes external code").
        2. Then a numbered list of findings. For each finding include:
        - Title (short label) and severity (Critical / High / Medium / Low),
        - Location (line numbers or function/class name),
        - What is wrong (concise), why it is wrong (concrete reasoning and example of failure), and how to reproduce the problem with a minimal input if applicable,
        - The exact fix: either a one-line patch, a small code snippet, or a diff (unified or inline) showing before → after,
        - Explanation of the fix and any consequences (e.g., backwards compatibility, edge cases introduced).
        3. After listing findings, provide:
        - "Patched code" section containing the full corrected code block (only the corrected file or snippet). Keep formatting and indentation exact.
        - A small "Regression tests / sanity checks" section: 3–6 concrete unit tests or assertions (with inputs & expected outputs) that verify the fixes.
        4. If any fix requires design choices or additional info (e.g., intended behavior unknown), make a best reasonable assumption and document it; if assumption is risky, mark it and show an alternative.

        CONSTRAINTS:
        - Do not hallucinate external dependencies or project context. If you reference libraries, ensure the references are implicitly present in the code or clearly propose them as optional enhancements.
        - Keep fixes minimal and safe; prefer explicit validation, clear error messages, and not-silent failures.

        Return only the structured content above in plain text and the corrected code block (no additional commentary).
        """


                run_code_action(prompt, "Debug Code", "Error Analysis")
        
        with opt_col:
            if st.button("Optimize", key="code_optimize"):
                prompt = f"""INSTRUCTION: You are a pragmatic performance engineer and software craftsman. Analyze the CODE below for improvements in time complexity, space complexity, correctness, readability, and maintainability. Identify hotspots and give safe, implementable optimizations.

    CODE:
    ```
    {st.session_state['current_code']}
    ```        
        REQUIREMENTS & OUTPUT FORMAT:
        1. Short summary (1–2 lines): language and the primary optimization opportunities you found.
        2. Profile-style "Hotspots" table (or short list) with entries:
        - Location (line numbers or function),
        - Why this is a hotspot (complexity or pattern, e.g., nested loops, repeated I/O, expensive API calls),
        - Estimated time/space complexity now and after recommended change (big-O notation; where exact constants matter, mention them).
        3. For each hotspot provide:
        - A precise, minimal code change or alternative approach (show code snippet / before→after diff),
        - Rationale (why it improves complexity or practical performance),
        - Any tradeoffs (readability vs performance, memory vs speed).
        4. Cross-cutting recommendations:
        - 5 checklist items for maintainability (naming, modularization, tests, docstrings, type hints),
        - 3 suggestions for runtime safety (input validation, resource limits, timeouts).
        5. Optional: If parallelism or algorithmic redesign is appropriate, provide a short, safe example (e.g., using a thread/process pool, batching, streaming) and explain concurrency considerations.
        6. End with a small "Benchmark plan" you could run locally: what to measure, test inputs, and expected measurable improvements.

        CONSTRAINTS:
        - Be conservative with changes that alter external behavior; prefer producing optional improved implementations alongside original code.
        - If a change depends on libraries (e.g., numpy, collections, asyncio), state that explicitly and keep the pure-stdlib alternative.

        Return only the structured text and code examples specified above.
        """

                run_code_action(prompt, "Optimize Code", "Optimization Suggestions")
        
        # --- Chat Interface ---
        st.markdown("---")
        st.markdown("""<h4 style='text-align: left; color: #33FF33;'>🎓 Chat with Code Expert</h4>""", unsafe_allow_html=True)
        
        for msg in st.session_state[messages_key]:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                
        if user_input := st.chat_input("Ask about code...", key="code_chat_input"):
            current_sess_id = st.session_state[session_id_key]
            update_session_title_if_new(current_sess_id, user_input)
            
            st.session_state[messages_key].append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.write(user_input)
            save_chat_message(user_id, current_sess_id, tab_name, "user", user_input)
            
            with st.spinner("Expert is analyzing..."):
                try:
                    llm = ChatGroq(model=selected_model, temperature=temperature, groq_api_key=os.getenv("GROQ_API_KEY"))
                    context = f"{SYSTEM_PROMPTS['code_explainer']}\nCurrent code:\n```\n{st.session_state.get('current_code', 'Not provided')}\n```"
                    
                    hist = [(m["role"], m["content"]) for m in st.session_state[messages_key][-10:]]
                    prompt = ChatPromptTemplate.from_messages([("system", context), *hist])
                    
                    response = llm.invoke(prompt.format_prompt().to_messages()).content
                    
                    st.session_state[messages_key].append({"role": "assistant", "content": response})
                    with st.chat_message("assistant"):
                        st.write(response)
                    
                    save_chat_message(user_id, current_sess_id, tab_name, "assistant", response)
                except Exception as e:
                    st.error(str(e))