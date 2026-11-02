from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")


def test_app_starts_without_errors():
    at = AppTest.from_file(APP, default_timeout=30).run()
    assert not at.exception
    assert at.title[0].value == "Resume Analyzer"


def test_analyze_without_a_resume_shows_a_warning():
    at = AppTest.from_file(APP, default_timeout=30).run()
    at.text_area[0].input("Python developer wanted").run()
    at.button[0].click().run()
    assert not at.exception
    assert any("Please upload a resume" in w.value for w in at.warning)
