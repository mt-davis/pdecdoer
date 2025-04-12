import streamlit as st
from chains.memory_chain import build_chat_chain
from utils.document_parser import load_and_split_document
from utils.session_tracker import track_activity
import tempfile
import os
from datetime import datetime
from components.ui_helpers import setup_page_config, sidebar_navigation, card, info_box, success_box

# Setup page with consistent styling
setup_page_config("Chat Memory")

# Add sidebar navigation
sidebar_navigation()

st.markdown("<p class='subtext' style='text-align: center; margin-bottom: 2rem;'>Chat with an AI assistant about any policy document.</p>", unsafe_allow_html=True)

# Main content area with card styling
card_content = """
<div>
    <h3>Upload Document for Chat</h3>
    <p>Upload a policy document or paste content to chat about.</p>
</div>
"""
card(card_content)

uploaded_file = st.file_uploader("Upload a policy document (PDF)", type="pdf")
manual_text = st.text_area("Or paste policy content below:", height=200)

# Add reading level selector
reading_level = st.select_slider(
    "Select your preferred reading level:",
    options=["Elementary (Ages 6-10)", "Middle School (Ages 11-13)", "High School (Ages 14-17)", "College", "Professional"],
    value="High School (Ages 14-17)",
    help="This will adjust the complexity of explanations to match your comfort level."
)

# Store chat history in session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if uploaded_file or manual_text:
    with st.spinner("Setting up chat session..."):
        if uploaded_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name
            docs = load_and_split_document(tmp_path)
            os.remove(tmp_path)
        else:
            docs = load_and_split_document(None, manual_text)

        # Get OpenAI API key from session state if available
        openai_api_key = st.session_state.get("openai_key", os.getenv("OPENAI_API_KEY"))
        
        chain = build_chat_chain(docs, openai_api_key, reading_level=reading_level)

        user_input = st.chat_input("Ask something about the policy...")
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            # Get the response from our chain
            response = chain(user_input)
            
            # Format the response with HTML for better readability
            formatted_response = f"""
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 10px;">
                <p style="font-size: 16px; color: #333;">{response}</p>
            </div>
            """
            
            # Add the response to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": response, "formatted_content": formatted_response})
            
            # Save conversation to reports for Export Report
            if 'reports' not in st.session_state:
                st.session_state.reports = {}

            # Only save if there's at least one exchange
            if len(st.session_state.chat_history) >= 2:
                # Format the conversation for the report
                conversation_text = ""
                for msg in st.session_state.chat_history:
                    prefix = "Q: " if msg["role"] == "user" else "A: "
                    conversation_text += f"{prefix}{msg['content']}\n\n"
                
                # Get document name or use default
                doc_name = uploaded_file.name if uploaded_file else "Chat Document"
                
                # Save to session state with timestamp
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                st.session_state.reports[f"Policy Chat: {doc_name} ({timestamp})"] = conversation_text
                
                # Track chat activity for session summary
                track_activity(
                    action="chatted about",
                    page_name="Chat Memory",
                    details={
                        "document_name": doc_name,
                        "query": user_input,
                        "reading_level": reading_level
                    }
                )
                
                # Show a success message only on new responses
                if len(st.session_state.chat_history) % 2 == 0:  # Even number means we just added a response
                    success_box("This conversation has been saved and can be accessed in the Export Report page.")

        # Display the chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                if message["role"] == "assistant" and "formatted_content" in message:
                    st.markdown(message["formatted_content"], unsafe_allow_html=True)
                else:
                    st.markdown(message["content"])
else:
    info_box("Upload or paste a document to begin chatting.")

# Add a footer
st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: var(--text-muted); font-size: 0.8rem;'>Adjust the reading level to customize how the AI explains policies to you.</p>", unsafe_allow_html=True)
