import streamlit as st
from utils.legislator_api import fetch_legislator_info

st.set_page_config(page_title="Legislator Lookup", layout="wide")
st.title("🧑‍⚖️ Legislator Lookup")

with st.sidebar:
    propublica_api_key = st.text_input("ProPublica API Key", type="password")

sponsor_name = st.text_input("Enter the legislator's full name (e.g. Jane Doe)")
lookup_button = st.button("Lookup Legislator")

if lookup_button and sponsor_name and propublica_api_key:
    with st.spinner("Fetching legislator profile and voting history..."):
        result = fetch_legislator_info(sponsor_name, propublica_api_key)

        if result:
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
            st.warning("No legislator found with that name. Please double-check spelling.")
else:
    st.info("Enter a full name and API key to begin.")
