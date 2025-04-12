import streamlit as st
from chains.ensemble_chain import build_ensemble_qa_chain
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
    page_title="Ensemble Decoder - PolicyCompassAI",
    page_icon="🤖",
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
st.markdown("<h1 class='page-title'>🤖 Ensemble Decoder</h1>", unsafe_allow_html=True)
st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# Add API key status indicators
openai_key_available = bool(st.session_state.get("openai_key") or openai_api_key)
claude_key_available = bool(st.session_state.get("anthropic_key") or anthropic_api_key)

openai_status = "✅ Available" if openai_key_available else "❌ Not Available"
claude_status = "✅ Available" if claude_key_available else "❌ Not Available"

st.markdown(f"""
<div style="max-width: 800px; margin: 0 auto;">
    <p class="subtext" style="text-align: center; margin-bottom: 1rem;">
        Get insights from multiple AI models working together.
    </p>
    <div style="display: flex; justify-content: center; gap: 20px; margin-bottom: 1rem;">
        <div style="padding: 5px 10px; border-radius: 5px; background-color: {'#e8f5e9' if openai_key_available else '#ffebee'};">
            <span style="font-weight: bold;">OpenAI:</span> {openai_status}
        </div>
        <div style="padding: 5px 10px; border-radius: 5px; background-color: {'#e8f5e9' if claude_key_available else '#ffebee'};">
            <span style="font-weight: bold;">Claude:</span> {claude_status}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

if not claude_key_available:
    st.warning("⚠️ Claude API key not found. The ensemble will fall back to using only OpenAI. Add a Claude API key in Settings to use ensemble features.")

# Add session history to sidebar
with st.sidebar:
    st.markdown("### 📝 Session History")
    if 'ensemble_history' not in st.session_state:
        st.session_state.ensemble_history = []
    
    if st.session_state.ensemble_history:
        for i, item in enumerate(st.session_state.ensemble_history[-5:]):  # Show last 5 queries
            with st.expander(f"Q: {item['question'][:30]}...", expanded=False):
                st.markdown(f"**Question:** {item['question']}")
                st.markdown(f"**Answer:** {item['answer']}")

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

# Add Analysis Mode selector
analysis_mode = st.selectbox(
    "Analysis Mode",
    ["General Overview", "Implementation Details", "Impact Analysis", "Compliance Check"],
    help="Choose a preset analysis mode to focus the ensemble analysis"
)

# Add query input
if 'query' not in st.session_state:
    st.session_state.query = ""

query = st.text_input(
    "What would you like to know about this policy?",
    value=st.session_state.query,
    placeholder="e.g., What are the main provisions of this policy?"
)

# Add Follow-up Questions section
if documents := st.session_state.get('last_analyzed_documents'):
    with st.expander("📝 Suggested Follow-up Questions", expanded=False):
        st.markdown("**Based on your document:**")
        follow_up_cols = st.columns(2)
        
        # Define follow-up questions based on analysis mode
        follow_up_questions = {
            "General Overview": [
                "What are the key objectives?",
                "Who are the main stakeholders?",
                "What is the timeline for implementation?"
            ],
            "Implementation Details": [
                "What are the specific steps for implementation?",
                "What resources are required?",
                "What are the key milestones?"
            ],
            "Impact Analysis": [
                "What are the expected outcomes?",
                "Are there any potential challenges?",
                "How will success be measured?"
            ],
            "Compliance Check": [
                "What are the compliance requirements?",
                "Are there any reporting obligations?",
                "What are the penalties for non-compliance?"
            ]
        }
        
        # Display relevant follow-up questions
        questions = follow_up_questions.get(analysis_mode, follow_up_questions["General Overview"])
        for i, q in enumerate(questions):
            col = follow_up_cols[i % 2]
            if col.button(q, key=f"follow_up_{i}"):
                st.session_state.query = q
                st.experimental_rerun()

# Model settings
st.markdown("### Model Settings")
col1, col2 = st.columns(2)

with col1:
    high_school_mode = st.toggle(
        "Explain at High School Level",
        help="Adjusts explanations to be suitable for high school students (grades 9-12)"
    )
    
with col2:
    ensemble_method = st.radio(
        "Synthesis Method",
        ["OpenAI", "Claude"],
        index=0,
        horizontal=True,
        help="Choose which model to use for synthesizing the responses",
        disabled=not claude_key_available
    )

# Analyze button
analyze_btn = st.button("Analyze with Ensemble", 
                       type="primary", 
                       disabled=not ((uploaded_file or manual_text) and query))

# Only show results when the button is clicked
if analyze_btn:
    if not (uploaded_file or manual_text):
        error_box("Please upload a document or paste policy content.")
    elif not query:
        error_box("Please enter a question to analyze.")
    else:
        with st.spinner("Analyzing policy document with multiple models..."):
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

                # Build ensemble chain and query
                ensemble_chain = build_ensemble_qa_chain(
                    documents, 
                    openai_api_key=st.session_state.get("openai_key", openai_api_key),
                    anthropic_api_key=st.session_state.get("anthropic_key", anthropic_api_key),
                    high_school_level=high_school_mode,
                    ensemble_with=ensemble_method.lower()
                )
                
                # Get ensemble response
                ensemble_result = ensemble_chain(query)
                
                # Extract responses
                openai_response = ensemble_result.get("openai_response", "No response from OpenAI")
                claude_response = ensemble_result.get("claude_response", "Claude API not available")
                ensemble_response = ensemble_result.get("ensemble_response", "Could not generate ensemble response")
                models_used = ensemble_result.get("models_used", ["Unknown"])
                
                # Save to history
                st.session_state.ensemble_history.append({
                    "question": query,
                    "answer": ensemble_response,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                
                # Save to reports for Export
                if 'reports' not in st.session_state:
                    st.session_state.reports = {}
                
                # Get document name
                doc_name = uploaded_file.name if uploaded_file else "Manual Text"
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                
                # Save individual and ensemble responses to reports
                report_content = f"""# {analysis_mode} Analysis: {doc_name}

## Analysis Context
- **Document:** {doc_name}
- **Analysis Mode:** {analysis_mode}
- **Question:** {query}
- **Timestamp:** {timestamp}

## Ensemble Response
{ensemble_response}

## Model Comparisons

### OpenAI Analysis
{openai_response}

"""
                if claude_response:
                    report_content += f"""
### Claude Analysis
{claude_response}

"""
                
                report_content += f"""
## Analysis Details
- **Models Used:** {', '.join(models_used)}
- **High School Level:** {"Enabled" if high_school_mode else "Disabled"}
- **Synthesis Method:** {ensemble_method}
"""
                
                st.session_state.reports[f"{analysis_mode} Analysis: {doc_name} ({timestamp})"] = report_content
                
                # Track activity for session summary
                track_activity(
                    action="ensemble analyzed",
                    page_name="Ensemble Decoder",
                    details={
                        "document_name": doc_name,
                        "query": query,
                        "models_used": ", ".join(models_used)
                    }
                )
                
                # Store policy content for voice summary
                doc_id = f"ensemble:{doc_name}"
                content = "\n".join([doc.page_content for doc in documents[:3]])  # Store first 3 chunks
                store_policy_content(
                    doc_id=doc_id,
                    content_type="ensemble",
                    content=content,
                    summary=ensemble_response[:500] if len(ensemble_response) > 500 else ensemble_response,
                    analysis=f"This analysis was generated using an ensemble of {', '.join(models_used)} models in response to the query: '{query}'."
                )
                
                # Display results
                if len(models_used) > 1:
                    # Show tabs with individual and ensemble responses
                    tabs = st.tabs(["Ensemble Response", "Analysis Comparison", "Individual Responses"])
                    
                    with tabs[0]:
                        st.markdown(f"### {analysis_mode} Analysis:")
                        st.markdown(ai_response(ensemble_response), unsafe_allow_html=True)
                    
                    with tabs[1]:
                        st.markdown("### Key Points Comparison")
                        comparison_cols = st.columns(2)
                        
                        with comparison_cols[0]:
                            st.markdown("#### OpenAI Analysis")
                            # Extract and display key points from OpenAI response
                            st.markdown(ai_response(openai_response), unsafe_allow_html=True)
                        
                        with comparison_cols[1]:
                            st.markdown("#### Claude Analysis")
                            # Extract and display key points from Claude response
                            st.markdown(ai_response(claude_response), unsafe_allow_html=True)
                    
                    with tabs[2]:
                        st.markdown("### Individual Model Responses")
                        with st.expander("OpenAI Full Response", expanded=False):
                            st.markdown(ai_response(openai_response), unsafe_allow_html=True)
                        
                        with st.expander("Claude Full Response", expanded=False):
                            st.markdown(ai_response(claude_response), unsafe_allow_html=True)
                else:
                    # Single model only - just show the response
                    st.markdown(f"### {analysis_mode} Analysis:")
                    st.markdown(ai_response(ensemble_response), unsafe_allow_html=True)
                    
                    if not claude_key_available:
                        st.info("Only OpenAI was used because Claude API key is not available. Add a Claude API key in Settings to use ensemble features.")
                
                # Store the analyzed documents for follow-up questions
                st.session_state.last_analyzed_documents = documents
                
                # Success message
                success_box(f"This {analysis_mode.lower()} analysis has been saved and can be accessed in the Export Report page.")
                
            except Exception as e:
                error_box(f"An error occurred during analysis: {str(e)}")
else:
    info_box("Upload a document and ask a question to get started.")

# Add a footer
st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: var(--text-muted); font-size: 0.8rem;'>Ensemble learning combines multiple AI models to provide more comprehensive and balanced analysis.</p>", unsafe_allow_html=True) 