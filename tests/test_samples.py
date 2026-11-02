"""Checks the whole pipeline on the sample files: every resume should rank its own job first."""
from pathlib import Path

import pytest

from src.extract import extract_text
from src.score import analyze
from src.skills import load_skills

DATA = Path(__file__).resolve().parent.parent / "data"

# resume file name (without extension) -> the job file name (without extension) it was written for
EXPECTED = {
    "resume_python_developer": "job_python_developer",
    "resume_data_analyst": "job_data_analyst",
    "resume_web_developer": "job_frontend_developer",
    "resume_marketing_executive": "job_digital_marketing",
    "resume_fresher_messy": "job_software_engineer_trainee",
    "resume_java_developer": "job_java_backend_engineer",
    "resume_devops_engineer": "job_cloud_devops_engineer",
    "resume_ml_engineer": "job_data_scientist",
    "resume_embedded_engineer": "job_embedded_firmware_engineer",
    "resume_ux_designer": "job_product_designer_ux",
}


def files_by_name(folder):
    """Map file name without extension -> path (if a job exists as .txt and .pdf, either one is fine)."""
    found = {}
    for path in sorted((DATA / folder).glob("*")):
        if path.suffix.lower() in (".txt", ".pdf"):
            found.setdefault(path.stem, path)
    return found


RESUMES = files_by_name("resumes")
JOBS = files_by_name("jobs")


@pytest.mark.parametrize("resume_name, expected_job", sorted(EXPECTED.items()))
def test_resume_ranks_its_own_job_first(resume_name, expected_job):
    if resume_name not in RESUMES or expected_job not in JOBS:
        pytest.skip("sample files are not in the data folder")
    patterns = load_skills()
    resume_text = extract_text(str(RESUMES[resume_name]))
    scores = {name: analyze(resume_text, extract_text(str(path)), patterns)["score"] for name, path in JOBS.items()}
    ranked = sorted(scores, key=scores.get, reverse=True)
    assert ranked[0] == expected_job, "best job was %s (%.0f%%), expected %s (%.0f%%)" % (
        ranked[0], scores[ranked[0]], expected_job, scores[expected_job])
    # and not by a hair
    runner_up = max(score for name, score in scores.items() if name != expected_job)
    assert scores[expected_job] - runner_up >= 10
