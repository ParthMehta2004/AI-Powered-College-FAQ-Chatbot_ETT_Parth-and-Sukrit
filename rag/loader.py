# PDF text extraction from raw data
from pathlib import Path
import PyPDF2

RAW_DATA_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract text from PDF file"""
    text = ""
    with pdf_path.open("rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            page_text = page.extract_text() or ""
            text += page_text + "\n"
    return text

def save_text(pdf_name: str, text: str) -> None:
    """Save extracted text to file"""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROCESSED_DIR / f"{pdf_name}.txt"
    out_path.write_text(text, encoding="utf-8")
