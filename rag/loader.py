import os
import PyPDF2

OUTPUT_DIR = "data/processed"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text

def save_text(filename, text):
    output_path = os.path.join(OUTPUT_DIR, f"{filename}.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
