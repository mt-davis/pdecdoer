import streamlit as st
from chains.rag_chain import build_qa_chain
from utils.document_parser import load_and_split_document
import tempfile
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

st.set_page_config(page_title="Policy Decoder", layout="wide")
st.title("📄 Upload a Policy Document")

# Sidebar
with st.sidebar:
    st.subheader("🔐 API Keys")
    openai_api_key = st.text_input("OpenAI API Key", type="password")

st.markdown("---")

uploaded_file = st.file_uploader("Upload a PDF document", type="pdf")
manual_text = st.text_area("Or paste policy content below:", height=200)
query = st.text_input("Ask a question about the policy")

eli5_mode = st.toggle("Explain Like I'm 5")

if (uploaded_file or manual_text) and query and openai_api_key:
    with st.spinner("Processing with OpenAI..."):

        # Load document content
        if uploaded_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_file_path = tmp_file.name
            documents = load_and_split_document(tmp_file_path)
            os.remove(tmp_file_path)
        else:
            documents = load_and_split_document(None, manual_text)

        # Build chain and query
        chain = build_qa_chain(documents, openai_api_key, eli5=eli5_mode)
        answer = chain.run(query)

        st.markdown("### AI Response:")
        st.success(answer)
else:
    st.info("Please upload or paste a document, enter your OpenAI key, and type a question.")
