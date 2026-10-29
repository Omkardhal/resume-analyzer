from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.extract import clean_text
from src.skills import load_skills, find_skills

# How much each part counts towards the final score (they add up to 1.0).
# Exact skills matter most when hiring, so they get the bigger share.
SKILL_WEIGHT = 0.7
TEXT_WEIGHT = 0.3


def text_similarity(resume_text, job_text):
    """How similar the two texts are overall, from 0 to 100.

    TF-IDF turns each text into a list of numbers (one per word, bigger for
    words that are more important). Cosine similarity then measures the angle
    between the two lists: a small angle means the texts talk about the same things.
    """
    if not resume_text.strip() or not job_text.strip():
        return 0.0
    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        vectors = vectorizer.fit_transform([resume_text, job_text])
    except ValueError:  # nothing useful left after removing common words like "the"
        return 0.0
    return float(cosine_similarity(vectors[0], vectors[1])[0][0]) * 100


def skill_match(resume_skills, job_skills):
    """Compare two sets of skills.

    Returns (percent of the job's skills the resume has, matched skills, missing skills).
    """
    matched = resume_skills & job_skills
    missing = job_skills - resume_skills
    percent = len(matched) / len(job_skills) * 100 if job_skills else 0.0
    return percent, matched, missing


def rating(score):
    """Turn a 0-100 score into a plain-English label."""
    if score >= 75:
        return "Strong match"
    if score >= 50:
        return "Good match"
    if score >= 25:
        return "Partial match"
    return "Weak match"


def analyze(resume_raw, job_raw, patterns=None):
    """Compare a resume and a job description (both as raw text).

    Pass `patterns` (from load_skills) when comparing many pairs, so the
    skills file is only read once.
    """
    if patterns is None:
        patterns = load_skills()

    resume_text = clean_text(resume_raw)
    job_text = clean_text(job_raw)

    resume_skills = find_skills(resume_text, patterns)
    job_skills = find_skills(job_text, patterns)
    skill_pct, matched, missing = skill_match(resume_skills, job_skills)
    text_pct = text_similarity(resume_text, job_text)

    if job_skills:
        final = SKILL_WEIGHT * skill_pct + TEXT_WEIGHT * text_pct
    else:
        # the job text has no skills we know about, so only the text score is usable
        final = text_pct

    return {
        "score": final,
        "rating": rating(final),
        "skill_score": skill_pct,
        "text_score": text_pct,
        "matched": sorted(matched, key=str.lower),
        "missing": sorted(missing, key=str.lower),
        "resume_skills": sorted(resume_skills, key=str.lower),
        "job_skills": sorted(job_skills, key=str.lower),
    }
