import sys

from src.extract import extract_text, clean_text
from src.skills import load_skills, find_skills


def skills_in(path, patterns):
    return find_skills(clean_text(extract_text(path)), patterns)


if len(sys.argv) != 3:
    print("Usage: python demo_day3.py <resume file> <job file>")
    sys.exit(1)

patterns = load_skills()
resume_skills = skills_in(sys.argv[1], patterns)
job_skills = skills_in(sys.argv[2], patterns)

matched = resume_skills & job_skills
missing = job_skills - resume_skills

print(f"Resume skills found ({len(resume_skills)}): {sorted(resume_skills, key=str.lower)}")
print(f"Job skills found ({len(job_skills)}): {sorted(job_skills, key=str.lower)}")
print(f"\nMatched ({len(matched)}): {sorted(matched, key=str.lower)}")
print(f"Missing from resume ({len(missing)}): {sorted(missing, key=str.lower)}")
if job_skills:
    print(f"\nSkill match: {len(matched) / len(job_skills) * 100:.0f}%")
