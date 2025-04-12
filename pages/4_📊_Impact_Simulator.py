import streamlit as st
from utils.document_parser import load_and_split_document
from utils.civic_data import simulate_impact_by_zip
from utils.session_tracker import track_activity, store_policy_content
from components.charts import display_impact_chart
import tempfile
import os
from dotenv import load_dotenv
from components.ui_helpers import setup_page_config, card, success_box, error_box, info_box, sidebar_navigation

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Setup page with consistent styling
setup_page_config("📊 Impact Simulator")
st.markdown("<p class='subtext' style='text-align: center; margin-bottom: 2rem;'>See how policies could affect you based on your personal information.</p>", unsafe_allow_html=True)

# Add sidebar navigation
sidebar_navigation()

# Main page title


with st.sidebar:
    card_content = """
    <div>
        <h3>Personal Information</h3>
        <p>This information will be used to personalize the impact simulation.</p>
    </div>
    """
    card(card_content)
    
    user_zip = st.text_input("ZIP Code", max_chars=5, help="Enter your 5-digit ZIP code")
    
    household_size = st.slider("Household Size", min_value=1, max_value=10, value=3, 
                               help="Number of people in your household")
    
    income_ranges = ["Less than $25,000", "$25,000-$50,000", "$50,000-$75,000", 
                     "$75,000-$100,000", "$100,000-$150,000", "More than $150,000"]
    income = st.select_slider("Annual Household Income", options=income_ranges, value="$50,000-$75,000")
    
    occupation_categories = ["Healthcare", "Education", "Technology", "Service Industry", 
                             "Manufacturing", "Government", "Finance", "Retail", 
                             "Construction", "Transportation", "Other"]
    occupation = st.selectbox("Primary Occupation", occupation_categories)
    
    has_health_insurance = st.checkbox("Has Health Insurance", value=True)
    
    housing_status = st.radio("Housing Status", ["Renter", "Homeowner", "Other"])

# Main content area with card styling
card_content = """
<div>
    <h3>Analyze Policy Impact</h3>
    <p>Upload a policy document or paste content to simulate its impact based on your profile.</p>
</div>
"""
card(card_content)

uploaded_file = st.file_uploader("Upload a bill to simulate its local impact (PDF)", type="pdf")
manual_text = st.text_area("Or paste bill content below:", height=200)
simulate_btn = st.button("Simulate Impact", type="primary", disabled=not (user_zip and (uploaded_file or manual_text)))

# Only show debug in developer mode or with a toggle
show_debug = st.checkbox("Show Debug Information", value=False)
if show_debug:
    st.write("### Debug:")
    col1, col2 = st.columns(2)
    with col1:
        show_variables = st.button("Show Variables")
    if show_variables:
        st.write(f"API Key from .env: {'Present' if openai_api_key else 'Missing'}")
        st.write(f"ZIP: {user_zip}")
        st.write(f"Household Size: {household_size}")
        st.write(f"Income: {income}")
        st.write(f"Occupation: {occupation}")
        st.write(f"Has Insurance: {has_health_insurance}")
        st.write(f"Housing: {housing_status}")

# Updated condition - only check for ZIP code and document
if simulate_btn:
    # Check for required inputs
    missing_inputs = []
    if not user_zip:
        missing_inputs.append("ZIP code")
    if not (uploaded_file or manual_text):
        missing_inputs.append("policy document (upload or paste)")
    if not openai_api_key:
        error_box("No OpenAI API key found. Please add it in the Settings page.")
        
    if missing_inputs:
        error_box(f"Missing required inputs: {', '.join(missing_inputs)}")
    else:
        with st.spinner("Simulating potential impacts for your area..."):
            if uploaded_file:
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(uploaded_file.read())
                        tmp_path = tmp.name
                    documents = load_and_split_document(tmp_path)
                    os.remove(tmp_path)
                except Exception as e:
                    error_box(f"Error processing PDF: {e}")
                    documents = []
            else:
                documents = load_and_split_document(None, manual_text)

            if not documents:
                error_box("No document content could be extracted. Please try a different document or paste text directly.")
            else:
                # Collect all user demographic data
                user_data = {
                    "zip": user_zip,
                    "household_size": household_size,
                    "income": income,
                    "occupation": occupation,
                    "has_health_insurance": has_health_insurance,
                    "housing_status": housing_status
                }

                try:
                    # Run simulation logic with expanded user data
                    result = simulate_impact_by_zip(documents, user_data, openai_api_key)
                    
                    # Main results card
                    card_content = f"""
                    <div>
                        <h3>Predicted Personal Impact</h3>
                        <p>{result['summary']}</p>
                    </div>
                    """
                    card(card_content)

                    st.markdown("### Visual Breakdown:")
                    display_impact_chart(result['categories'])
                    
                    # Show more detailed impact by category
                    st.markdown("### Detailed Impact Assessment:")
                    for category, details in result.get('details', {}).items():
                        with st.expander(f"Impact on {category}", expanded=False):
                            st.write(details)
                            
                    # Save simulation results to session state for Export Report
                    if 'reports' not in st.session_state:
                        st.session_state.reports = {}
                    
                    # Format the simulation results for the report
                    report_content = f"""
                    # Personal Impact Simulation Results
                    
                    ## Summary
                    {result['summary']}
                    
                    ## Detailed Impact Assessment
                    """
                    
                    # Add details for each category
                    for category, details in result.get('details', {}).items():
                        report_content += f"\n### Impact on {category}\n{details}\n"
                    
                    # Get document name or use default
                    doc_name = uploaded_file.name if uploaded_file else "Impact Simulation"
                    
                    # Save to session state with timestamp
                    from datetime import datetime
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                    st.session_state.reports[f"Impact Simulation: {user_zip} ({timestamp})"] = report_content
                    
                    # Track activity for session summary
                    track_activity(
                        action="simulated impact",
                        page_name="Impact Simulator",
                        details={
                            "document_name": doc_name,
                            "zip_code": user_zip,
                            "income": income,
                            "occupation": occupation
                        }
                    )
                    
                    # Store impact analysis for policy content summary
                    doc_id = f"impact:{doc_name}_zip_{user_zip}"
                    
                    # Create a summary of the impact analysis
                    summary = result["summary"]
                    
                    # Generate a more detailed analysis with recommendations
                    analysis_parts = []
                    analysis_parts.append(f"This impact analysis was generated for ZIP code {user_zip} with household size {household_size}, income level {income}, and occupation in {occupation}.")
                    
                    # Add recommendations based on impact categories
                    if "Healthcare" in result.get("categories", {}):
                        score = result["categories"]["Healthcare"]
                        if score > 70:
                            analysis_parts.append(f"The high impact score on healthcare ({score}%) suggests this policy would significantly affect your healthcare costs and access. Consider researching whether other policies might mitigate these impacts.")
                    
                    if "Housing" in result.get("categories", {}):
                        score = result["categories"]["Housing"]
                        if score > 50:
                            analysis_parts.append(f"With a housing impact score of {score}%, consider researching housing assistance programs that might be available during policy implementation.")
                    
                    # Add general recommendation
                    analysis_parts.append("For a more complete analysis, consider comparing this policy with alternatives and examining historical outcomes of similar policies in comparable regions.")
                    
                    analysis = " ".join(analysis_parts)
                    
                    # Format the content for storage
                    content = f"Summary: {summary}\n\n"
                    for category, details in result.get("details", {}).items():
                        content += f"Impact on {category}: {details}\n\n"
                    
                    # Store the policy content
                    store_policy_content(
                        doc_id=doc_id,
                        content_type="impact",
                        content=content,
                        summary=summary,
                        analysis=analysis
                    )
                    
                    # Notify user it's been saved for export
                    success_box("This simulation has been saved and can be accessed in the Export Report page.")
                            
                except Exception as e:
                    error_box(f"An error occurred during simulation: {str(e)}")
else:
    info_box("Enter your ZIP code and personal information, then upload a bill to simulate its impact on you.")

# Add a footer
st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
