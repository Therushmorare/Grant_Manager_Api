from weasyprint import HTML
from io import BytesIO


def generate_pdf_from_html(html_content):
    pdf_file = BytesIO()

    HTML(string=html_content).write_pdf(pdf_file)

    pdf_file.seek(0)
    return pdf_file