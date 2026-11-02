import json

import pytest

from src.extract import clean_text
from src.skills import SKILLS_FILE, find_skills, load_skills


@pytest.fixture(scope="module")
def patterns():
    return load_skills()


def skills_in(text, patterns):
    return find_skills(clean_text(text), patterns)


# ---------- matching rules ----------

@pytest.mark.parametrize("text, expected", [
    # a skill must not be found inside a longer word
    ("mysql and postgresql only", {"MySQL", "PostgreSQL"}),     # no plain SQL
    ("I know javascript", {"JavaScript"}),                       # no Java
    ("github workflows", {"GitHub"}),                            # no Git
    ("only c++ here", {"C++"}),                                  # no plain C
    ("C, C++ and C#", {"C", "C++", "C#"}),
    ("C/C++ programming", {"C", "C++"}),
    # punctuation and spelling variants
    ("we use Node.js.", {"Node.js"}),                            # no plain "node", period is fine
    ("Experience with SQL.", {"SQL"}),
    ("CI/CD pipelines", {"CI/CD"}),
    ("UI/UX designer", {"UI/UX"}),
    ("scikit-learn and sklearn", {"Scikit-learn"}),
    ("REST APIs and RESTful API design", {"REST API"}),
    ("Spring Boot microservices", {"Spring Boot", "Microservices"}),
    ("ARM Cortex-M and CAN protocols", {"ARM Cortex-M", "CAN Bus"}),
    ("react.js and reactjs", {"React"}),
    ("Python3 and ES6", {"Python"}),
    ("Node JS, React JS and Vue JS", {"Node.js", "React", "Vue.js"}),
    ("strong in algorithm design and data structure", {"Algorithms", "Data Structures"}),
    ("created wireframe and prototype", {"Wireframing", "Prototyping"}),
    ("AI/ML projects", {"Machine Learning"}),
    ("data visualisation with powerbi", {"Data Visualization", "Power BI"}),
    # messy formatting
    ("PYTHON, SQL\r\nJAVA\t(basic)", {"Python", "SQL", "Java"}),
    ("Python and SQL", {"Python", "SQL"}),
    ("ﬁle handling and ﬂask apps", {"File Handling", "Flask"}),   # PDF ligatures
    ("designed in ﬁgma", {"Figma"}),
    # things that must not match
    ("email: someone@example.com", set()),
    ("", set()),
])
def test_skill_matching(text, expected, patterns):
    assert skills_in(text, patterns) == expected


@pytest.mark.parametrize("text, expected", [
    # words that are also ordinary English
    ("I excel at teamwork and strive to excel", set()),
    ("to excel in my career", set()),
    ("I want to express my interest in this role", set()),
    ("sketch wireframes on paper first", {"Wireframing"}),
    # ...but the real skills still match
    ("Advanced Excel, Power BI", {"Excel", "Power BI"}),
    ("proficient in Excel and SQL", {"Excel", "SQL"}),
    ("Node.js, Express, MongoDB", {"Node.js", "Express", "MongoDB"}),
    ("Figma, Sketch, Adobe XD", {"Figma", "Sketch", "Adobe XD"}),
])
def test_words_that_are_also_plain_english(text, expected, patterns):
    assert skills_in(text, patterns) == expected


# ---------- the skills file itself ----------

def load_raw():
    with open(SKILLS_FILE, encoding="utf-8") as f:
        return json.load(f)


def test_skills_file_is_valid():
    data = load_raw()
    assert len(data) > 100
    for skill, aliases in data.items():
        assert isinstance(aliases, list), skill
        assert all(isinstance(a, str) and a.strip() for a in aliases), skill


def test_no_name_or_alias_is_used_by_two_skills():
    seen = {}
    for skill, aliases in load_raw().items():
        for name in [skill] + aliases:
            key = clean_text(name)
            assert key not in seen or seen[key] == skill, "%r is used by both %s and %s" % (name, seen[key], skill)
            seen[key] = skill


def test_every_skill_can_be_found_by_its_own_name(patterns):
    for skill in load_raw():
        assert skill in skills_in("experience with %s" % skill, patterns), skill


def test_every_alias_finds_its_skill(patterns):
    for skill, aliases in load_raw().items():
        for alias in aliases:
            assert skill in skills_in("experience with %s" % alias, patterns), (skill, alias)
