import streamlit as st
import os
from dotenv import load_dotenv
from utils.legislator_api import fetch_legislator_info
from utils.session_tracker import track_activity
from components.ui_helpers import setup_page_config, sidebar_navigation

# Load environment variables
load_dotenv()

# Setup page with consistent styling
setup_page_config(" 🧑‍⚖️Legislator Lookup")
st.markdown("<p class='subtext' style='text-align: center; margin-bottom: 2rem;'>Look up information about legislators and their voting records.</p>", unsafe_allow_html=True)

# Add sidebar navigation
sidebar_navigation()



# Get API key from session state or fallback to environment variable
propublica_api_key = st.session_state.get("propublica_key", os.getenv("PROPUBLICA_API_KEY", ""))

sponsor_name = st.text_input("Enter the legislator's full name (e.g. Jane Doe)")
lookup_button = st.button("Lookup Legislator")

if lookup_button and sponsor_name and propublica_api_key:
    with st.spinner("Fetching legislator profile and voting history..."):
        result = fetch_legislator_info(sponsor_name, propublica_api_key)

        if result:
            # Track successful lookup activity
            track_activity(
                action="looked up legislator",
                page_name="Legislator Lookup", 
                details={
                    "legislator_name": sponsor_name,
                    "party": result['party'],
                    "state": result['state']
                }
            )
            
            st.markdown(f"### {result['name']}")
            st.markdown(f"- **Party**: {result['party']}")
            st.markdown(f"- **State**: {result['state']}")
            st.markdown(f"- **District**: {result['district']}")
            st.markdown("### Bio:")
            st.info(result['bio'])

            st.markdown("### Recent Votes:")
            for vote in result['votes']:
                st.markdown(f"✅ {vote}")
        else:
            # Track failed lookup activity
            track_activity(
                action="attempted to look up legislator",
                page_name="Legislator Lookup",
                details={
                    "legislator_name": sponsor_name,
                    "result": "not found"
                }
            )
            
            st.warning("No legislator found with that name. Please double-check spelling.")
else:
    st.info("Enter a full name and make sure your ProPublica API key is set in the Settings page.")

# Add a footer
st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
