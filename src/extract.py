import re
import pdfplumber


def extract_text(file_path):
    """Read text from a PDF or a plain text file."""
    if file_path.lower().endswith(".pdf"):
        with pdfplumber.open(file_path) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
        return "\n".join(pages)
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def clean_text(text):
    """Lowercase and strip junk, but keep characters like + # . so c++, c# and node.js survive."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9+#.\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()