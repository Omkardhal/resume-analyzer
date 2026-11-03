"""Command-line version of the Resume Analyzer.

Usage:
  python cli.py <resume file> <job file>   detailed report for one resume and one job
  python cli.py <resume file>              rank every job in data/jobs for this resume

Resumes and jobs can be .pdf or .txt files.
"""
import sys
from pathlib import Path

from src.extract import extract_text
from src.score import SKILL_WEIGHT, TEXT_WEIGHT, analyze
from src.skills import load_skills

JOBS_DIR = Path(__file__).resolve().parent / "data" / "jobs"
USAGE = __doc__.split("Usage:")[1].split("Resumes and jobs")[0].strip("\n")


def read(path):
    """Read a file, or stop with a short message that says what is wrong."""
    try:
        text = extract_text(path)
    except FileNotFoundError:
        sys.exit(f"File not found: {path}")
    except Exception:
        sys.exit(f"Could not read {path}. Try another PDF, or a .txt file.")
    if not text.strip():
        sys.exit(f"No text found in {path}. If it is a PDF, it may be a scanned image.")
    return text


def one_pair(resume_path, job_path):
    result = analyze(read(resume_path), read(job_path))
    print(f"Final match score : {result['score']:.0f}%  ({result['rating']})")
    print(f"  Skill match     : {result['skill_score']:.0f}%   (counts {SKILL_WEIGHT:.0%} of the final score)")
    print(f"  Text similarity : {result['text_score']:.0f}%   (counts {TEXT_WEIGHT:.0%} of the final score)")
    print(f"\nMatched skills ({len(result['matched'])}): {', '.join(result['matched']) or 'none'}")
    print(f"Missing skills ({len(result['missing'])}): {', '.join(result['missing']) or 'none'}")


def rank_jobs(resume_path):
    resume_raw = read(resume_path)
    patterns = load_skills()
    rows, seen = [], set()
    for job_path in sorted(JOBS_DIR.glob("*")):
        if job_path.suffix.lower() not in (".txt", ".pdf") or job_path.stem in seen:
            continue  # a job saved as both .txt and .pdf is only scored once
        seen.add(job_path.stem)
        result = analyze(resume_raw, read(str(job_path)), patterns)
        rows.append((result["score"], result["rating"], job_path.name))
    if not rows:
        sys.exit(f"No job files found in {JOBS_DIR}")
    rows.sort(reverse=True)
    print(f"Best matching jobs for {Path(resume_path).name}:\n")
    for score, label, name in rows:
        print(f"  {score:5.0f}%  {label:14s} {name}")


def main(argv):
    if len(argv) == 2:
        one_pair(argv[0], argv[1])
    elif len(argv) == 1:
        rank_jobs(argv[0])
    else:
        sys.exit("Usage:\n" + USAGE)


if __name__ == "__main__":
    main(sys.argv[1:])
