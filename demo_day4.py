import glob
import os
import sys

from src.extract import extract_text
from src.skills import load_skills
from src.score import analyze, SKILL_WEIGHT, TEXT_WEIGHT

USAGE = """Usage:
  python demo_day4.py <resume file> <job file>   detailed report for one pair
  python demo_day4.py <resume file>              rank every job in data/jobs for this resume"""


def one_pair(resume_path, job_path):
    result = analyze(extract_text(resume_path), extract_text(job_path))
    print(f"Final match score : {result['score']:.0f}%  ({result['rating']})")
    print(f"  Skill match     : {result['skill_score']:.0f}%   (counts {SKILL_WEIGHT:.0%} of the final score)")
    print(f"  Text similarity : {result['text_score']:.0f}%   (counts {TEXT_WEIGHT:.0%} of the final score)")
    print(f"\nMatched skills ({len(result['matched'])}): {', '.join(result['matched']) or 'none'}")
    print(f"Missing skills ({len(result['missing'])}): {', '.join(result['missing']) or 'none'}")


def rank_jobs(resume_path):
    patterns = load_skills()
    resume_raw = extract_text(resume_path)
    rows = []
    for job_path in sorted(glob.glob("data/jobs/*")):
        result = analyze(resume_raw, extract_text(job_path), patterns)
        rows.append((result["score"], result["rating"], os.path.basename(job_path)))
    rows.sort(reverse=True)
    print(f"Best matching jobs for {os.path.basename(resume_path)}:\n")
    for score, label, name in rows:
        print(f"  {score:5.0f}%  {label:14s} {name}")


if len(sys.argv) == 3:
    one_pair(sys.argv[1], sys.argv[2])
elif len(sys.argv) == 2:
    rank_jobs(sys.argv[1])
else:
    print(USAGE)
    sys.exit(1)
