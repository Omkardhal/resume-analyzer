import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def run_cli(*args):
    return subprocess.run([sys.executable, "cli.py", *args], cwd=ROOT, capture_output=True, text=True)


def test_cli_without_arguments_prints_usage():
    result = run_cli()
    assert result.returncode == 1
    assert "python cli.py <resume file> <job file>" in result.stderr


def test_cli_reports_a_missing_file_without_a_traceback():
    result = run_cli("no_such_resume.pdf", "no_such_job.txt")
    assert result.returncode == 1
    assert "File not found" in result.stderr
    assert "Traceback" not in result.stderr


def test_cli_reports_an_empty_file(tmp_path):
    empty = tmp_path / "empty.txt"
    empty.write_text("")
    result = run_cli(str(empty), str(empty))
    assert result.returncode == 1
    assert "No text found" in result.stderr


def test_cli_compares_one_resume_with_one_job(tmp_path):
    resume = tmp_path / "resume.txt"
    resume.write_text("Python developer with SQL and Git experience.")
    job = tmp_path / "job.txt"
    job.write_text("We need Python, SQL, Git and Docker skills.")
    result = run_cli(str(resume), str(job))
    assert result.returncode == 0
    assert "Final match score" in result.stdout
    assert "Matched skills (3): Git, Python, SQL" in result.stdout
    assert "Missing skills (1): Docker" in result.stdout


def test_cli_ranks_the_jobs_in_the_data_folder(tmp_path):
    if not any((ROOT / "data" / "jobs").glob("*.txt")):
        pytest.skip("no sample jobs in data/jobs")
    resume = tmp_path / "resume.txt"
    resume.write_text("Python developer with SQL, Git, Flask and Docker experience.")
    result = run_cli(str(resume))
    assert result.returncode == 0
    assert "Best matching jobs for resume.txt" in result.stdout
