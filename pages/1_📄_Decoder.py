import streamlit as st
from chains.rag_chain import build_qa_chain
from utils.document_parser import load_and_split_document
from utils.session_tracker import track_activity, store_policy_content
import tempfile
import os
from dotenv import load_dotenv
from components.ui_helpers import setup_page_config, card, success_box, error_box, info_box, ai_response, sidebar_navigation
from datetime import datetime

# Load .env file
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

# Configure the page
st.set_page_config(
    page_title="Decoder - PolicyCompassAI",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
from components.ui_helpers import apply_custom_css
apply_custom_css()

# With multipage apps, the sidebar navigation is handled automatically by Streamlit
# But we'll keep this for consistency with current app structure
sidebar_navigation()

# Header - simplified as page config already sets page title
st.markdown("<h1 class='page-title'>📄 Policy Decoder</h1>", unsafe_allow_html=True)
st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# Add session history to sidebar
with st.sidebar:
    st.markdown("### 📝 Session History")
    if 'decoder_history' not in st.session_state:
        st.session_state.decoder_history = []
    
    if st.session_state.decoder_history:
        for i, item in enumerate(st.session_state.decoder_history[-5:]):  # Show last 5 queries
            with st.expander(f"Q: {item['question'][:30]}...", expanded=False):
                st.markdown(f"**Question:** {item['question']}")
                st.markdown(f"**Answer:** {item['answer']}")

# Mobile-friendly layout
st.markdown("""
<div style="max-width: 800px; margin: 0 auto;">
    <p class="subtext" style="text-align: center; margin-bottom: 2rem;">
        Upload a policy document and ask questions to understand it better.
    </p>
</div>
""", unsafe_allow_html=True)

# Main content area with card styling
card_content = """
<div>
    <h3>Upload Document</h3>
    <p>Upload a PDF document or paste policy content below to analyze.</p>
</div>
"""
card(card_content)

uploaded_file = st.file_uploader("Upload a PDF document", type="pdf")
manual_text = st.text_area("Or paste policy content below:", height=150)

# Question input with improved styling
st.markdown("### Ask a Question")
query = st.text_input("What would you like to know about this policy?", 
                     placeholder="e.g., What are the main provisions of this policy?")

col1, col2 = st.columns([3, 1])
with col1:
    eli5_mode = st.toggle("Explain Like I'm 5", help="Simplifies explanations for easier understanding")
with col2:
    analyze_btn = st.button("Analyze", type="primary", disabled=not ((uploaded_file or manual_text) and query))

# Analysis section
if analyze_btn:
    if not (uploaded_file or manual_text):
        error_box("Please upload a document or paste content before asking a question.")
    elif not query:
        error_box("Please enter a question about the policy.")
    elif not openai_api_key:
        error_box("OpenAI API key is required. Please add it in the sidebar.")
    else:
        with st.spinner("Analyzing policy document..."):
            try:
                # Load document content
                if uploaded_file:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                        tmp_file.write(uploaded_file.read())
                        tmp_file_path = tmp_file.name
                    documents = load_and_split_document(tmp_file_path)
                    os.remove(tmp_file_path)
                    
                    # Show extracted content in an expander
                    with st.expander("View Extracted Content", expanded=False):
                        st.markdown("### Document Content:")
                        for i, doc in enumerate(documents):
                            st.markdown(f"**Page {i+1}:**")
                            st.markdown(f"```{doc.page_content[:300]}... (truncated)```")
                else:
                    documents = load_and_split_document(None, manual_text)

                # Get API key from session state if available
                if st.session_state.get("openai_key"):
                    openai_api_key = st.session_state.get("openai_key")

                # Build chain and query
                chain = build_qa_chain(documents, openai_api_key, eli5=eli5_mode)
                answer = chain(query)
                
                # Save to history
                st.session_state.decoder_history.append({
                    "question": query,
                    "answer": answer,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                
                # Save to reports for Export
                if 'reports' not in st.session_state:
                    st.session_state.reports = {}
                
                # Get document name
                doc_name = uploaded_file.name if uploaded_file else "Manual Text"
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                
                # Save to reports
                st.session_state.reports[f"Policy Question: {doc_name} ({timestamp})"] = f"Q: {query}\n\nA: {answer}"
                
                # Track activity for session summary
                track_activity(
                    action="analyzed",
                    page_name="Policy Decoder",
                    details={
                        "document_name": doc_name,
                        "query": query,
                        "result": "successful analysis"
                    }
                )
                
                # Store policy content for voice summary
                doc_id = f"decoder:{doc_name}"
                content = "\n".join([doc.page_content for doc in documents[:3]])  # Store first 3 chunks
                store_policy_content(
                    doc_id=doc_id,
                    content_type="document",
                    content=content,
                    summary=answer[:500] if len(answer) > 500 else answer,  # Truncate long answers
                    analysis=f"This analysis was generated in response to the query: '{query}'. Further research could explore related policy documents or impact assessments."
                )
                
                # Display result with improved styling
                st.markdown("### Analysis Result:")
                st.markdown(ai_response(answer), unsafe_allow_html=True)
                
                # Success message
                success_box("This analysis has been saved and can be accessed in the Export Report page.")
                
            except Exception as e:
                error_box(f"An error occurred during analysis: {str(e)}")
else:
    info_box("Upload a document and ask a question to get started.")

# Add a footer
st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: var(--text-muted); font-size: 0.8rem;'>Need help understanding complex policy language? Try the 'Explain Like I'm 5' toggle for simplified explanations.</p>", unsafe_allow_html=True)
