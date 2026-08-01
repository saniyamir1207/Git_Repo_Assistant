import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Page setup
st.set_page_config(
    page_title="Git Repo Assistant",
    page_icon="🐙",
    layout="wide"
)

#  Get client
@st.cache_resource
def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("🔑 GEMINI_API_KEY not found in .env file!")
        st.stop()
    # Alternatively, passing api_key directly:
    return genai.Client(api_key=api_key)

client = get_gemini_client()

# System instructions to keep Gemini focused on Git & GitHub
SYSTEM_INSTRUCTION = """
You are expert Git & GitHub Assistant. Your goal is to guide developers in managing repositories, 
understanding Git concepts, and learning commands.
- Provide clear, well-structured, and concise answers.
- Format all terminal commands and code blocks properly using markdown.
- Give real-world tips and warn users about risky operations (e.g., git push --force).
"""

# App Header
st.title("🐙 Git Repo Assistant")
st.caption("Powered by Google Gemini & Streamlit")

# Navigation Sidebar
st.sidebar.title("Navigation")
option = st.sidebar.radio(
    "Choose a Feature:",
    [
        "1. Git Command Explainer",
        "2. Repository Setup Guide",
        "3. Git Learning Assistant"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 *Tip:* Need help with a tricky merge conflict or rebase? Ask in the Learning Assistant tab!")

# Helper function to call Gemini
def generate_git_response(prompt):
    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.3,
            ),
        )

        if hasattr(response, "text") and response.text:
            return response.text

        return response.candidates[0].content.parts[0].text

    except Exception as e:
        return f"❌ Error: {e}"
# ==============================================================================
# FEATURE 1: GIT COMMAND EXPLAINER
# ==============================================================================
if option == "1. Git Command Explainer":
    st.header("⚡ Git Command Explainer")
    st.write("Enter any Git command to get a clear breakdown of what it does, its flags, and when to use it.")

    command_input = st.text_input(
        "Enter Git Command:",
        placeholder="e.g., git commit -m 'Initial commit' or git rebase -i HEAD~3"
    )

    if st.button("Explain Command", type="primary"):
        if command_input.strip():
            with st.spinner("Analyzing command..."):
                prompt = f"""
                Explain the following Git command in detail:
                Command: {command_input}

                Please structure the explanation as follows:
                1. *Summary*: What this exact command does in simple terms.
                2. *Flag Breakdown*: Break down what each flag or argument (if any) does.
                3. *When to use it*: Common scenarios where this command is useful.
                4. *Caution/Warning*: Any potential risks (e.g., losing uncommitted work) if applicable.
                """
                explanation = generate_git_response(prompt)
                st.markdown(explanation)
        else:
            st.warning("Please enter a command first.")

# ==============================================================================
# FEATURE 2: REPOSITORY SETUP GUIDE
# ==============================================================================
elif option == "2. Repository Setup Guide":
    st.header("🛠️ Repository Setup Guide")
    st.write("Generate a customized step-by-step walkthrough to set up your project repo.")

    col1, col2 = st.columns(2)
    with col1:
        project_type = st.selectbox(
            "Project Type / Language:",
            ["Python", "Node.js / React", "C / C++", "Java", "Web (HTML/CSS/JS)", "Other"]
        )
        platform = st.radio("Remote Platform:", ["GitHub", "GitLab", "Bitbucket", "Local Only"])

    with col2:
        include_gitignore = st.checkbox("Include recommended .gitignore content", value=True)
        include_readme = st.checkbox("Include .md template outline", value=True)
        is_existing = st.radio("Starting Point:", ["Brand new local folder", "Existing code on local machine"])

    if st.button("Generate Setup Steps", type="primary"):
        with st.spinner("Creating setup guide..."):
            prompt = f"""
            Provide a complete step-by-step walkthrough for setting up a Git repository with these details:
            - *Project Type*: {project_type}
            - *Platform*: {platform}
            - *Starting point*: {is_existing}
            - *Include .gitignore*: {include_gitignore}
            - *Include README outline*: {include_readme}

            Provide exact terminal commands to initialize, add, commit, and link to the remote repository.
            If .gitignore or README was requested, provide code blocks for those files as well.
            """
            guide = generate_git_response(prompt)
            st.markdown(guide)

# ==============================================================================
# FEATURE 3: GIT LEARNING ASSISTANT
# ==============================================================================
elif option == "3. Git Learning Assistant":
    st.header("🎓 Git Learning Assistant")
    st.write("Ask any conceptual questions about Git, workflows, or troubleshooting errors.")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi! I'm your Git mentor. Ask me anything—like 'What is the staging area?', 'How do I resolve a merge conflict?', or 'Explain Git Flow vs Trunk-Based Development'."}
        ]

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if user_prompt := st.chat_input("Ask a Git question..."):
        # Display user message
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response_text = generate_git_response(user_prompt)
                st.markdown(response_text)
                
        st.session_state.messages.append({"role": "assistant", "content": response_text})


