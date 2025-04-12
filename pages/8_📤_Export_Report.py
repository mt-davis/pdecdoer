import streamlit as st
import os
from utils.report_generator import generate_pdf
from utils.session_tracker import track_activity
import tempfile
from datetime import datetime
from components.ui_helpers import setup_page_config, card, success_box, error_box, info_box, sidebar_navigation

# Setup page with consistent styling
setup_page_config("Export Report")

# Add sidebar navigation
sidebar_navigation()

st.markdown("""
<div style="max-width: 800px; margin: 0 auto;">
    <p class="subtext" style="text-align: center; margin-bottom: 2rem;">
        Compile and download reports from your saved policy analyses.
    </p>
</div>
""", unsafe_allow_html=True)

# Initialize session state for storing reports
if 'reports' not in st.session_state:
    st.session_state.reports = {}

# Add a section to save content from other pages
card_content = """
<div>
    <h3>Save Analysis from Other Pages</h3>
    <p>Add content from other sections of the app to include in your report.</p>
</div>
"""
card(card_content)

col1, col2 = st.columns([3, 1])
with col1:
    section_name = st.text_input("Section Name", placeholder="e.g., Bill Comparison")
    section_content = st.text_area("Analysis Content", height=150, placeholder="Paste content from other pages to save it for your report")
with col2:
    st.write("")
    st.write("")
    if st.button("Save Section", type="primary"):
        if section_name and section_content:
            st.session_state.reports[section_name] = section_content
            
            # Track activity for saving a section
            track_activity(
                action="saved report section",
                page_name="Export Report",
                details={
                    "section_name": section_name,
                    "content_length": len(section_content)
                }
            )
            
            success_box(f"Saved '{section_name}' to your report!")
        else:
            error_box("Please provide both a section name and content.")

# Show saved sections
if st.session_state.reports:
    card_content = """
    <div>
        <h3>Saved Sections</h3>
        <p>View and manage your saved analysis sections.</p>
    </div>
    """
    card(card_content)
    
    for section, content in st.session_state.reports.items():
        with st.expander(section):
            st.text(content)
            if st.button("Remove", key=f"remove_{section}"):
                del st.session_state.reports[section]
                st.experimental_rerun()

# Report customization
st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
card_content = """
<div>
    <h3>Report Customization</h3>
    <p>Customize your report with title, author, and other metadata.</p>
</div>
"""
card(card_content)

# Report metadata
col1, col2 = st.columns(2)
with col1:
    report_title = st.text_input("Report Title", value="Policy Analysis Report")
    author = st.text_input("Author Name", placeholder="Your name (optional)")
with col2:
    date = st.date_input("Report Date", value=datetime.now())
    filename = st.text_input("Filename", value="policy_report.pdf")

# Add new content directly
card_content = """
<div>
    <h3>Additional Content</h3>
    <p>Add notes or supplementary information to your report.</p>
</div>
"""
card(card_content)
add_content = st.text_area("Add notes or additional content to your report", height=150, placeholder="Any additional notes you want to include in your report")

# Report generation
st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
col1, col2 = st.columns([3, 1])
with col1:
    card_content = """
    <div>
        <h3>Generate Report</h3>
        <p>Create and download your compiled report as a PDF.</p>
    </div>
    """
    card(card_content)
    
    # Warning if no content
    if not st.session_state.reports and not add_content:
        info_box("Your report is empty. Please add content before generating.")
    
    # Report contents preview
    if st.session_state.reports:
        st.write("Your report will include these sections:")
        for section in st.session_state.reports.keys():
            st.write(f"- {section}")
    
    if add_content:
        st.write("- Additional notes and content")
with col2:
    st.write("")
    st.write("")
    export_button = st.button("Generate PDF Report", type="primary", disabled=(not st.session_state.reports and not add_content))

# Report generation process
if export_button:
    with st.spinner("Generating your report..."):
        # Prepare report content
        report_content = {}
        
        # Add all saved sections
        for section, content in st.session_state.reports.items():
            report_content[section] = content
        
        # Add additional content if provided
        if add_content:
            report_content["Additional Notes"] = add_content
        
        # Prepare metadata
        metadata = {
            "title": report_title,
            "author": author,
            "date": date.strftime("%B %d, %Y")
        }
        
        # Generate the PDF
        file_path = generate_pdf(report_content, filename, metadata)
        
        if file_path:
            # Track activity for generating a report
            track_activity(
                action="generated report",
                page_name="Export Report",
                details={
                    "report_title": report_title,
                    "sections": len(report_content),
                    "author": author if author else "Anonymous"
                }
            )
            
            success_box("Report generated successfully!")
            with open(file_path, "rb") as f:
                st.download_button(
                    label="Download Report",
                    data=f,
                    file_name=filename,
                    mime="application/pdf"
                )
            # Clean up the temporary file
            try:
                os.remove(file_path)
            except:
                pass
        else:
            error_box("Failed to generate the PDF. Please try again.")

# Add a footer
st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: var(--text-muted); font-size: 0.8rem;'>Export your policy analysis reports for sharing, presentation, or further reference.</p>", unsafe_allow_html=True)
