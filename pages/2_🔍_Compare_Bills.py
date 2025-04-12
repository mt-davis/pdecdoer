import os
import streamlit as st
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from utils.document_parser import load_and_split_document
from utils.session_tracker import track_activity, store_policy_content
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.documents import Document
import tempfile
from datetime import datetime
from components.ui_helpers import setup_page_config, card, success_box, error_box, info_box, ai_response, sidebar_navigation, apply_custom_css

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Configure the page
st.set_page_config(
    page_title="Compare Bills - PolicyCompassAI",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
apply_custom_css()

# With multipage apps, the sidebar navigation is handled automatically by Streamlit
# But we'll keep this for consistency with current app structure
sidebar_navigation()

# Header - simplified as page config already sets page title
st.markdown("<h1 class='page-title'>🔍 Compare Bills</h1>", unsafe_allow_html=True)
st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

st.markdown("""
<div style="max-width: 800px; margin: 0 auto;">
    <p class="subtext" style="text-align: center; margin-bottom: 2rem;">
        Upload or paste two policy documents to compare differences and similarities.
    </p>
</div>
""", unsafe_allow_html=True)

# Optional Claude integration
claude_llm = None
if ANTHROPIC_API_KEY:
    try:
        from langchain_anthropic import ChatAnthropic
        claude_llm = ChatAnthropic(api_key=ANTHROPIC_API_KEY, model_name="claude-3-sonnet-20240229")
    except Exception as e:
        print("Claude setup failed:", e)


def compare_policies(docs1, docs2, openai_api_key=OPENAI_API_KEY):
    # Get API key from session state if available
    if st.session_state.get("openai_key"):
        openai_api_key = st.session_state.get("openai_key")
        
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.3, openai_api_key=openai_api_key)

    content1 = "\n".join([d.page_content for d in docs1])
    content2 = "\n".join([d.page_content for d in docs2])
    
    # Check for large documents and limit size if necessary
    MAX_CHARS = 10000  # Limiting each document to about 10K characters to avoid token limits
    
    if len(content1) > MAX_CHARS:
        content1 = content1[:MAX_CHARS] + f"\n\n[Note: Document 1 was truncated from {len(content1)} characters to {MAX_CHARS} characters due to size limits.]"
    
    if len(content2) > MAX_CHARS:
        content2 = content2[:MAX_CHARS] + f"\n\n[Note: Document 2 was truncated from {len(content2)} characters to {MAX_CHARS} characters due to size limits.]"
    
    # Create a single document with both bills
    combined_content = f"BILL 1:\n{content1}\n\nBILL 2:\n{content2}"
    combined_doc = Document(page_content=combined_content)
    
    # Create a summary prompt template
    prompt = PromptTemplate(
        input_variables=["context"],
        template="""
        You are a legislative analyst. Compare the two policy texts below and summarize:
        - Key similarities
        - Major differences
        - Potential impact
        
        Keep your analysis concise and focused on the most important points.

        {context}
        """
    )

    # Use the new method to create a stuff documents chain
    chain = create_stuff_documents_chain(llm, prompt)
    
    try:
        # Process the document directly
        response = chain.invoke({"input": "", "context": [combined_doc]})
        
        # Extract the result
        if isinstance(response, dict) and 'output_text' in response:
            return response['output_text']
        return str(response)
    except Exception as e:
        if "rate_limit_exceeded" in str(e) or "context window" in str(e).lower():
            # If we hit rate limits even with truncation, return a helpful message with document summaries
            return f"""
            The documents are too large to be compared in detail. Here's a brief summary of each:
            
            DOCUMENT 1 (first {min(1000, len(content1))} characters):
            {content1[:1000]}...
            
            DOCUMENT 2 (first {min(1000, len(content2))} characters):
            {content2[:1000]}...
            
            To compare these documents, please try with shorter texts or split them into smaller sections.
            """
        else:
            # Re-raise other exceptions
            raise e


# UI Code for the page - using card layout for better mobile experience
card_content1 = """
<div>
    <h3>Document 1</h3>
    <p>Upload or paste the first policy document to compare.</p>
</div>
"""

card_content2 = """
<div>
    <h3>Document 2</h3>
    <p>Upload or paste the second policy document to compare.</p>
</div>
"""

col1, col2 = st.columns(2)

with col1:
    card(card_content1)
    uploaded_file1 = st.file_uploader("Upload first policy document (PDF)", type="pdf", key="file1")
    manual_text1 = st.text_area("Or paste first policy text:", height=200, key="text1")

with col2:
    card(card_content2)
    uploaded_file2 = st.file_uploader("Upload second policy document (PDF)", type="pdf", key="file2")
    manual_text2 = st.text_area("Or paste second policy text:", height=200, key="text2")

compare_btn = st.button("Compare Documents", type="primary")

if compare_btn:
    # Check if we have content for both documents
    has_doc1 = uploaded_file1 is not None or manual_text1.strip() != ""
    has_doc2 = uploaded_file2 is not None or manual_text2.strip() != ""
    
    if not has_doc1 or not has_doc2:
        error_box("Please provide content for both documents to compare.")
    else:
        with st.spinner("Analyzing and comparing documents..."):
            try:
                # Process document 1
                if uploaded_file1:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(uploaded_file1.read())
                        tmp_path = tmp.name
                    docs1 = load_and_split_document(tmp_path)
                    os.remove(tmp_path)
                else:
                    docs1 = load_and_split_document(None, manual_text1)
                    
                # Process document 2
                if uploaded_file2:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(uploaded_file2.read())
                        tmp_path = tmp.name
                    docs2 = load_and_split_document(tmp_path)
                    os.remove(tmp_path)
                else:
                    docs2 = load_and_split_document(None, manual_text2)
                
                # Compare the documents
                comparison_result = compare_policies(docs1, docs2, OPENAI_API_KEY)
                
                # Save result to session state for Export Report
                if 'reports' not in st.session_state:
                    st.session_state.reports = {}
                
                # Get document names or use defaults
                doc1_name = uploaded_file1.name if uploaded_file1 else "Manual Text 1"
                doc2_name = uploaded_file2.name if uploaded_file2 else "Manual Text 2"
                report_title = f"Bill Comparison: {doc1_name} vs {doc2_name}"

                # Save to session state with timestamp
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                st.session_state.reports[f"Bill Comparison ({timestamp})"] = comparison_result
                
                # Track activity for session summary
                track_activity(
                    action="compared",
                    page_name="Compare Bills",
                    details={
                        "document_name": f"{doc1_name} vs {doc2_name}",
                        "result": "successful comparison"
                    }
                )
                
                # Debug print for session tracking
                print(f"Tracked comparison activity. Total activities: {len(st.session_state.get('user_activities', []))}")
                
                # Store comparison for policy content summary
                doc_id = f"comparison:{doc1_name}_vs_{doc2_name}"
                
                # Extract insights from comparison result to create analysis
                analysis = ""
                if "similarities" in comparison_result.lower() or "differences" in comparison_result.lower():
                    analysis = "Based on this comparison, consider how the different approaches might impact implementation and stakeholder support. Research how similar policies have been enacted in other jurisdictions could provide valuable context."
                else:
                    analysis = "Consider researching the historical context of these policies and evaluating which approach might be more effective based on available evidence."
                
                # Store the policy content
                store_policy_content(
                    doc_id=doc_id,
                    content_type="comparison",
                    content=comparison_result,
                    summary=comparison_result[:500] if len(comparison_result) > 500 else comparison_result,  # Truncate long responses
                    analysis=analysis
                )

                # Display results
                st.markdown("## Comparison Results:")
                st.markdown(ai_response(comparison_result), unsafe_allow_html=True)
                
                # Notify user it's been saved for export
                success_box("This comparison has been saved and can be accessed in the Export Report page.")
                
            except Exception as e:
                error_box(f"An error occurred during comparison: {str(e)}")
else:
    info_box("Upload or paste two policy documents to compare them side by side.")

# Add a footer
st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: var(--text-muted); font-size: 0.8rem;'>Compare policies to identify key similarities, differences, and potential impacts.</p>", unsafe_allow_html=True)
