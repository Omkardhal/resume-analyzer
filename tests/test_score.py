import pytest

from src.score import SKILL_WEIGHT, TEXT_WEIGHT, analyze, rating, skill_match, text_similarity

RESUME = "Python developer with SQL, Docker and AWS experience. Built REST APIs with Flask and used Git every day."
JOB = "We need a Python developer. Required: Python, SQL, Docker, Kubernetes, REST API and Git."
MARKETING_RESUME = "Digital marketer with SEO, Google Ads, Mailchimp and content marketing experience, and strong copywriting."


# ---------- text similarity ----------

def test_weights_add_up_to_one():
    assert SKILL_WEIGHT + TEXT_WEIGHT == pytest.approx(1.0)


def test_identical_texts_are_100_percent_similar():
    assert text_similarity("python sql developer", "python sql developer") == pytest.approx(100)


def test_unrelated_texts_are_0_percent_similar():
    assert text_similarity("python sql developer", "marketing seo copywriting") == pytest.approx(0)


def test_similarity_of_empty_text_is_0():
    assert text_similarity("", "python") == 0
    assert text_similarity("python", "   ") == 0


def test_similarity_of_only_common_words_does_not_crash():
    assert text_similarity("the and of", "the and of") == 0


# ---------- skill match ----------

def test_skill_match_numbers():
    percent, matched, missing = skill_match({"Python", "SQL", "Git"}, {"Python", "SQL", "Docker", "AWS"})
    assert percent == pytest.approx(50)
    assert matched == {"Python", "SQL"}
    assert missing == {"Docker", "AWS"}


def test_extra_skills_on_the_resume_do_not_hurt():
    percent, _, missing = skill_match({"Python", "SQL", "Git", "Docker"}, {"Python"})
    assert percent == 100
    assert missing == set()


def test_skill_match_when_the_job_lists_no_skills():
    percent, matched, missing = skill_match({"Python"}, set())
    assert percent == 0
    assert matched == set() and missing == set()


# ---------- rating labels ----------

@pytest.mark.parametrize("score, label", [
    (0, "Weak match"), (24.9, "Weak match"),
    (25, "Partial match"), (49.9, "Partial match"),
    (50, "Good match"), (74.9, "Good match"),
    (75, "Strong match"), (100, "Strong match"),
])
def test_rating_boundaries(score, label):
    assert rating(score) == label


# ---------- analyze: the whole comparison ----------

def test_analyze_returns_all_fields_in_range():
    result = analyze(RESUME, JOB)
    assert set(result) == {"score", "rating", "skill_score", "text_score",
                           "matched", "missing", "resume_skills", "job_skills"}
    for key in ("score", "skill_score", "text_score"):
        assert 0 <= result[key] <= 100


def test_analyze_finds_matched_and_missing_skills():
    result = analyze(RESUME, JOB)
    assert set(result["matched"]) == {"Python", "SQL", "Docker", "REST API", "Git"}
    assert result["missing"] == ["Kubernetes"]


def test_analyze_is_directional():
    # the question is "does the resume cover the job?", so swapping the two changes the answer
    forward = analyze(RESUME, JOB)
    backward = analyze(JOB, RESUME)
    assert forward["missing"] != backward["missing"]


def test_a_matching_resume_scores_higher_than_an_unrelated_one():
    assert analyze(RESUME, JOB)["score"] > analyze(MARKETING_RESUME, JOB)["score"] + 30


def test_comparing_a_document_with_itself_scores_100():
    assert analyze(RESUME, RESUME)["score"] == pytest.approx(100)


def test_empty_resume_scores_zero():
    assert analyze("", JOB)["score"] == 0


def test_empty_job_scores_zero():
    assert analyze(RESUME, "")["score"] == 0


def test_job_without_known_skills_uses_the_text_score_only():
    result = analyze(RESUME, "We want a friendly person who loves teamwork and learning new things.")
    assert result["job_skills"] == []
    assert result["score"] == pytest.approx(result["text_score"])
