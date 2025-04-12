import streamlit as st
from utils.document_parser import load_and_split_document
from utils.civic_data import simulate_impact_by_zip
from components.charts import display_impact_chart
import tempfile
import os

st.set_page_config(page_title="Impact Simulator", layout="wide")
st.title("📊 Civic Impact Simulator")

with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    user_zip = st.text_input("Enter your ZIP code", max_chars=5)

st.markdown("---")

uploaded_file = st.file_uploader("Upload a bill to simulate its local impact (PDF)", type="pdf")
manual_text = st.text_area("Or paste bill content below:", height=200)
simulate_btn = st.button("Simulate Impact")

if simulate_btn and user_zip and openai_api_key:
    if uploaded_file or manual_text:
        with st.spinner("Simulating potential impacts for your area..."):
            if uploaded_file:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name
                documents = load_and_split_document(tmp_path)
                os.remove(tmp_path)
            else:
                documents = load_and_split_document(None, manual_text)

            # Run simulation logic
            result = simulate_impact_by_zip(documents, user_zip, openai_api_key)
            st.markdown("### Predicted Local Impact:")
            st.success(result['summary'])

            st.markdown("### Visual Breakdown:")
            display_impact_chart(result['categories'])
    else:
        st.warning("Upload a document or paste some text.")
else:
    st.info("Enter your ZIP code and upload a bill to simulate its impact.")
