from fpdf import FPDF
import os
import tempfile
from datetime import datetime

class PolicyReportPDF(FPDF):
    def header(self):
        # Logo (if we had one)
        # self.image('logo.png', 10, 8, 33)
        # Set font
        self.set_font('Arial', 'B', 16)
        # Title
        self.cell(0, 10, 'Policy Decoder Report', 0, 1, 'C')
        # Date
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, f'Generated on {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 1, 'C')
        # Line break
        self.ln(10)
    
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Set font
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

def generate_pdf(content, filename, metadata=None):
    """
    Generate a PDF report with policy analysis content.
    
    Args:
        content (str or dict): Text content or structured content with sections
        filename (str): Output filename
        metadata (dict): Optional metadata like title, author, etc.
    
    Returns:
        str: Path to the generated PDF file
    """
    pdf = PolicyReportPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Add metadata if provided
    if metadata:
        title = metadata.get('title', 'Policy Analysis')
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, title, 0, 1, 'L')
        
        # Add other metadata
        pdf.set_font("Arial", 'I', 10)
        if 'date' in metadata:
            pdf.cell(0, 10, f"Date: {metadata['date']}", 0, 1, 'L')
        if 'author' in metadata:
            pdf.cell(0, 10, f"Author: {metadata['author']}", 0, 1, 'L')
        
        pdf.ln(5)
    
    # Process content
    if isinstance(content, dict):
        # Structured content with sections
        for section_title, section_content in content.items():
            # Section header
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, section_title, 0, 1, 'L')
            
            # Section content
            pdf.set_font("Arial", '', 11)
            lines = section_content.split('\n')
            for line in lines:
                # Split long lines to fit in the page
                if line.strip():
                    pdf.multi_cell(0, 6, line)
                else:
                    pdf.ln(4)  # Empty line
            
            pdf.ln(5)  # Space between sections
    else:
        # Simple text content
        pdf.set_font("Arial", '', 11)
        lines = content.split('\n')
        for line in lines:
            if line.strip():
                pdf.multi_cell(0, 6, line)
            else:
                pdf.ln(4)  # Empty line
    
    # Create a temporary file
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            file_path = tmp.name
        
        pdf.output(file_path)
        return file_path
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None
