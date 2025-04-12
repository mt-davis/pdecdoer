from fpdf import FPDF
import os

def generate_pdf(text, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    lines = text.split('\n')
    for line in lines:
        pdf.multi_cell(0, 10, line)

    file_path = os.path.join("/tmp", filename)
    try:
        pdf.output(file_path)
        return file_path
    except:
        return None
