import fitz  # PyMuPDF
from docx import Document

def parse_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()

def parse_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().strip()

def parse_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
