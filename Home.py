import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
import os
from components.ui_helpers import apply_custom_css, sidebar_navigation, card, info_box
from utils.session_tracker import initialize_session_tracker

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize session state for tracking activities
initialize_session_tracker()

# Setup page with consistent styling
st.set_page_config(
    page_title="PolicyCompassAI - Home",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Apply custom CSS
apply_custom_css()

# Note: With the new multipage app structure, Streamlit will automatically handle the sidebar navigation
# The sidebar_navigation call can eventually be removed, but keep for now to maintain compatibility
sidebar_navigation()



# Header
st.markdown("<h1 class='page-title'>🧠 PolicyCompassAI</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtext' style='text-align: center; font-size: 1.2rem; color: var(--text-muted); margin-bottom: 1.5rem;'>Make sense of complex policies with AI-powered insights</p>", unsafe_allow_html=True)

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# Create a dashboard layout with feature cards
st.markdown("## Start Exploring")

col1, col2, col3 = st.columns(3)

with col1:
    card("""
    <h3>📄 Decode Policy Documents</h3>
    <p>Upload a policy document and ask questions to understand it better.</p>
    <a href='/Decoder' target='_self'>
        <button style='background-color: var(--primary-color); color: white; border: none; 
        padding: 0.5rem 1rem; border-radius: var(--border-radius); margin-top: 1rem; 
        font-weight: 500; cursor: pointer; width: 100%;'>Start Decoding</button>
    </a>
    """)

with col2:
    card("""
    <h3>🔍 Compare Bills</h3>
    <p>Upload two documents to see a side-by-side comparison of their key differences.</p>
    <a href='/Compare_Bills' target='_self'>
        <button style='background-color: var(--primary-color); color: white; border: none; 
        padding: 0.5rem 1rem; border-radius: var(--border-radius); margin-top: 1rem; 
        font-weight: 500; cursor: pointer; width: 100%;'>Compare Now</button>
    </a>
    """)

with col3:
    card("""
    <h3>📊 Impact Simulator</h3>
    <p>See how a policy could affect you based on your personal information.</p>
    <a href='/Impact_SSimulator' target='_self'>
        <button style='background-color: var(--primary-color); color: white; border: none; 
        padding: 0.5rem 1rem; border-radius: var(--border-radius); margin-top: 1rem; 
        font-weight: 500; cursor: pointer; width: 100%;'>Simulate Impact</button>
    </a>
    """)

# Second row of cards
col1, col2, col3 = st.columns(3)

with col1:
    card("""
    <h3>💬 Chat with AI</h3>
    <p>Have a conversation about policy documents with our AI assistant.</p>
    <a href='/Chat_Memory' target='_self'>
        <button style='background-color: var(--primary-color); color: white; border: none; 
        padding: 0.5rem 1rem; border-radius: var(--border-radius); margin-top: 1rem; 
        font-weight: 500; cursor: pointer; width: 100%;'>Start Chatting</button>
    </a>
    """)

with col2:
    card("""
    <h3>🎮 Test Your Knowledge</h3>
    <p>Take a quiz to test your understanding of policy concepts.</p>
    <a href='/Civic_Quiz' target='_self'>
        <button style='background-color: var(--primary-color); color: white; border: none; 
        padding: 0.5rem 1rem; border-radius: var(--border-radius); margin-top: 1rem; 
        font-weight: 500; cursor: pointer; width: 100%;'>Take Quiz</button>
    </a>
    """)

with col3:
    card("""
    <h3>📤 Export Your Analysis</h3>
    <p>Create a professional PDF report from your policy analysis.</p>
    <a href='/Export_Report' target='_self'>
        <button style='background-color: var(--primary-color); color: white; border: none; 
        padding: 0.5rem 1rem; border-radius: var(--border-radius); margin-top: 1rem; 
        font-weight: 500; cursor: pointer; width: 100%;'>Export Report</button>
    </a>
    """)

# Additional information section
st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
st.markdown("## About PolicyCompassAI")

with st.expander("Read more about our platform", expanded=False):
    st.markdown("""
    PolicyCompassAI is a powerful, AI-enhanced civic education app that helps everyday people understand how government policies affect their personal and community lives. By using large language models (LLMs), live data from government and economic sources, and user personalization, the app translates complex policy information into clear, relevant, and actionable insights.
    
    ### Key Features:
    - Upload and analyze policy documents
    - Compare multiple bills side-by-side
    - Visualize how policies impact your specific situation
    - Get information about legislators and voting records
    - Test your policy knowledge with interactive quizzes
    - Export professional reports for sharing insights
    
    This tool aims to increase civic participation by making government policies more accessible and understandable to all citizens.
    """)

# Add a footer
st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: var(--text-muted); font-size: 0.8rem;'>© 2023 PolicyCompassAI | Powered by AI for civic engagement</p>", unsafe_allow_html=True)

# Add debug expander for session state
with st.expander("Debug Session State", expanded=False):
    st.write("### Session Tracking Status")
    
    if "user_activities" in st.session_state:
        activity_count = len(st.session_state.user_activities)
        st.success(f"Session tracking is active with {activity_count} recorded activities")
        
        if activity_count > 0:
            st.write("#### Recent Activities:")
            for i, activity in enumerate(st.session_state.user_activities[-5:]):  # Show last 5
                st.write(f"{i+1}. {activity['timestamp']} - {activity['page']}: {activity['action']}")
    else:
        st.warning("No activities are being tracked yet. Session tracking may not be initialized properly.")
    
    # Add test activity button
    if st.button("Add Test Activity"):
        from utils.session_tracker import track_activity
        track_activity(
            action="tested session tracking",
            page_name="Home Page",
            details={"test": True, "timestamp": str(st.session_state.get("_accessed_time", "unknown"))}
        )
        st.experimental_rerun()