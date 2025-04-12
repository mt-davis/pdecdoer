import streamlit as st
from utils.report_generator import generate_pdf

st.set_page_config(page_title="Export Report", layout="wide")
st.title("📤 Export Summary Report")

text_input = st.text_area("Paste your policy summary or analysis to export:", height=300)
filename = st.text_input("Choose a filename:", value="policy_summary.pdf")
export_button = st.button("Export as PDF")

if export_button and text_input:
    with st.spinner("Generating your report..."):
        file_path = generate_pdf(text_input, filename)
        if file_path:
            with open(file_path, "rb") as f:
                st.download_button("Download Report", f, file_name=filename)
        else:
            st.error("Failed to generate PDF. Please try again.")
else:
    st.info("Paste content and choose a filename to export.")
