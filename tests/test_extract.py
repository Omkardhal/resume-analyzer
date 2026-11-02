import codecs

import pytest

from src import extract
from src.extract import clean_text, extract_text


# ---------- clean_text ----------

def test_clean_text_lowercases_and_collapses_whitespace():
    assert clean_text("  Python \n\n  Developer\t ") == "python developer"


def test_clean_text_keeps_plus_hash_and_dot():
    assert clean_text("C++, C# and Node.js") == "c++ c# and node.js"


def test_clean_text_turns_slashes_into_spaces():
    assert clean_text("CI/CD and UI/UX") == "ci cd and ui ux"


def test_clean_text_splits_pdf_ligatures_back_into_letters():
    # PDFs often store "fi" and "fl" as single characters; without this, "Figma" would become "gma"
    assert clean_text("ﬁle and ﬂask and ﬁgma") == "file and flask and figma"


def test_clean_text_handles_special_spaces_and_dashes():
    assert clean_text("Python and SQL–Java") == "python and sql java"


def test_clean_text_of_empty_text_is_empty():
    assert clean_text("") == ""
    assert clean_text("   \n\t") == ""


# ---------- extract_text with text files ----------

def test_extract_text_reads_a_text_file(tmp_path):
    f = tmp_path / "resume.txt"
    f.write_text("Python developer", encoding="utf-8")
    assert extract_text(str(f)) == "Python developer"


def test_extract_text_survives_bad_bytes_in_a_text_file(tmp_path):
    f = tmp_path / "odd.txt"
    f.write_bytes(b"Python \xff\xfe developer")
    text = extract_text(str(f))
    assert "Python" in text and "developer" in text


def test_extract_text_of_an_empty_text_file_is_empty(tmp_path):
    f = tmp_path / "empty.txt"
    f.write_text("", encoding="utf-8")
    assert extract_text(str(f)) == ""


def test_extract_text_drops_the_utf8_bom(tmp_path):
    f = tmp_path / "bom.txt"
    f.write_bytes(codecs.BOM_UTF8 + "Python developer".encode("utf-8"))
    assert extract_text(str(f)) == "Python developer"


@pytest.mark.parametrize("encoding", ["utf-16", "utf-16-le", "utf-16-be"])
def test_extract_text_reads_utf16_files(tmp_path, encoding):
    # Windows Notepad's "Unicode" option saves UTF-16. Read as UTF-8, no skill would be found.
    f = tmp_path / "notepad.txt"
    f.write_bytes("Skills: Python, SQL and Docker".encode(encoding))
    assert extract_text(str(f)) == "Skills: Python, SQL and Docker"


def test_extract_text_reads_old_windows_files(tmp_path):
    f = tmp_path / "old.txt"
    f.write_bytes("Résumé – Python “SQL”".encode("cp1252"))
    assert extract_text(str(f)) == "Résumé – Python “SQL”"


# ---------- extract_text with PDFs ----------

def make_pdf(text):
    """Build a tiny one-page PDF containing `text`, so these tests need no sample files."""
    content = ("BT /F1 12 Tf 72 720 Td (%s) Tj ET" % text).encode()
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R "
        b"/Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length %d >>\nstream\n" % len(content) + content + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    pdf = b"%PDF-1.4\n"
    offsets = []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf += b"%d 0 obj\n" % number + body + b"\nendobj\n"
    xref_start = len(pdf)
    pdf += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    for offset in offsets:
        pdf += b"%010d 00000 n \n" % offset
    pdf += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objects) + 1, xref_start)
    return pdf


def test_extract_text_reads_a_real_pdf(tmp_path):
    f = tmp_path / "resume.pdf"
    f.write_bytes(make_pdf("Python developer with SQL"))
    assert "Python developer with SQL" in extract_text(str(f))


def test_extract_text_of_a_pdf_without_text_is_empty(tmp_path):
    # this is what a scanned resume looks like to the program
    f = tmp_path / "blank.pdf"
    f.write_bytes(make_pdf(""))
    assert extract_text(str(f)).strip() == ""


class FakePage:
    def __init__(self, text):
        self._text = text

    def extract_text(self):
        return self._text


class FakePDF:
    def __init__(self, pages):
        self.pages = [FakePage(t) for t in pages]

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def test_extract_text_removes_pdf_bullet_artifacts(monkeypatch):
    monkeypatch.setattr(extract.pdfplumber, "open", lambda path: FakePDF(["(cid:127) Python\n(cid:127) SQL"]))
    text = extract_text("resume.pdf")
    assert "cid" not in text
    assert "Python" in text and "SQL" in text


def test_extract_text_joins_pages_and_survives_pages_without_text(monkeypatch):
    monkeypatch.setattr(extract.pdfplumber, "open", lambda path: FakePDF(["page one", None, "page three"]))
    text = extract_text("RESUME.PDF")  # an upper-case extension still counts as a PDF
    assert "page one" in text and "page three" in text
