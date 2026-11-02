import codecs
import re
import unicodedata

import pdfplumber


def read_text_file(file_path):
    """Read a text file whatever encoding it was saved in.

    Most files are UTF-8, but a file saved as "Unicode" by Windows Notepad is UTF-16.
    Read as UTF-8 it turns into one stray character between every letter, so no skill is found.
    """
    with open(file_path, "rb") as f:
        raw = f.read()
    if raw.startswith((codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE)):
        return raw.decode("utf-16", errors="replace")
    if b"\x00" in raw[:200]:  # UTF-16 without a BOM: every other byte is 0
        return raw.decode("utf-16-be" if raw[0] == 0 else "utf-16-le", errors="replace")
    try:
        return raw.decode("utf-8-sig")  # also drops the BOM that some editors add
    except UnicodeDecodeError:
        return raw.decode("cp1252", errors="replace")  # older Windows files


def extract_text(file_path):
    """Read text from a PDF or a plain text file."""
    if file_path.lower().endswith(".pdf"):
        with pdfplumber.open(file_path) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
        text = "\n".join(pages)
        # Some PDFs store bullet points as "(cid:127)" instead of a real character.
        # Remove them, or they show up as fake shared words ("cid", "127") in the comparison.
        return re.sub(r"\(cid:\d+\)", " ", text)
    return read_text_file(file_path)


def clean_text(text):
    """Normalise and lowercase text and strip junk, but keep + # . so c++, c# and node.js survive."""
    # PDFs often store "fi" and "fl" as single ligature characters, which would turn "Figma" into "gma".
    # NFKC splits them back into plain letters (and turns full-width and non-breaking characters into normal ones).
    text = unicodedata.normalize("NFKC", text)
    text = text.lower()
    text = re.sub(r"[^a-z0-9+#.\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()
