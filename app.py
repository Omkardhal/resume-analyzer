import os
import tempfile

import streamlit as st

from src.extract import extract_text
from src.score import analyze, SKILL_WEIGHT, TEXT_WEIGHT

st.set_page_config(page_title="Resume Analyzer", page_icon="📄", layout="wide")

st.title("Resume Analyzer")
st.write(
    "Upload your resume, paste a job description, and see how well they match "
    "and which skills your resume is missing."
)


def read_upload(uploaded_file):
    """Save the uploaded file to a temporary file so extract_text() can read it."""
    suffix = os.path.splitext(uploaded_file.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getvalue())
        path = tmp.name
    try:
        return extract_text(path)
    finally:
        os.remove(path)


left, right = st.columns(2)
with left:
    st.subheader("1. Your resume")
    resume_file = st.file_uploader("Upload a PDF or text file", type=["pdf", "txt"])
with right:
    st.subheader("2. The job description")
    job_text = st.text_area("Paste the job description here", height=250)

if st.button("Analyze", type="primary"):
    if resume_file is None or not job_text.strip():
        st.warning("Please upload a resume and paste a job description first.")
        st.stop()

    try:
        resume_text = read_upload(resume_file)
    except Exception:
        st.error("Could not read that file. Try another PDF, or save your resume as a .txt file.")
        st.stop()

    if not resume_text.strip():
        st.error(
            "No text found in this resume. It may be a scanned image. "
            "Please upload a text-based PDF instead."
        )
        st.stop()

    result = analyze(resume_text, job_text)

    st.divider()
    st.header("Results")

    col1, col2, col3 = st.columns(3)
    col1.metric("Overall match", f"{result['score']:.0f}%")
    col2.metric(
        "Skill match",
        f"{result['skill_score']:.0f}%",
        help=f"Share of the job's skills found in your resume. Counts {SKILL_WEIGHT:.0%} of the overall score.",
    )
    col3.metric(
        "Text similarity",
        f"{result['text_score']:.0f}%",
        help=f"How similar the wording is (TF-IDF and cosine similarity). Counts {TEXT_WEIGHT:.0%} of the overall score.",
    )
    st.progress(min(int(result["score"]), 100))

    show_rating = {
        "Strong match": st.success,
        "Good match": st.info,
        "Partial match": st.warning,
        "Weak match": st.error,
    }
    show_rating[result["rating"]](result["rating"])

    if not result["job_skills"]:
        st.warning(
            "We could not find any known skills in this job description, "
            "so the score is based on text similarity only."
        )

    matched_col, missing_col = st.columns(2)
    with matched_col:
        st.subheader(f"Matched skills ({len(result['matched'])})")
        st.write(", ".join(result["matched"]) or "None")
    with missing_col:
        st.subheader(f"Missing skills ({len(result['missing'])})")
        st.write(
            ", ".join(result["missing"])
            or "None. Your resume covers every skill we found in the job description."
        )
