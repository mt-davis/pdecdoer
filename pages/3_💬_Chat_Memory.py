import streamlit as st
from chains.memory_chain import build_chat_chain
from utils.document_parser import load_and_split_document
import tempfile
import os

st.set_page_config(page_title="Chat with Memory", layout="wide")
st.title("💬 Chat With a Policy Document")

st.markdown("---")

uploaded_file = st.file_uploader("Upload a policy document (PDF)", type="pdf")
manual_text = st.text_area("Or paste policy content below:", height=200)

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

        chain = build_chat_chain(docs)  # No need to pass key explicitly

        user_input = st.chat_input("Ask something about the policy...")
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            response = chain.invoke(user_input)
            st.session_state.chat_history.append({"role": "assistant", "content": response})

        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
else:
    st.info("Upload or paste a document to begin chatting.")
