from src.learn import (DEFAULT_CATEGORY, DEFAULT_TIP, category_of, coverage_by_category,
                       learning_tip, load_learning)
from src.skills import load_skills

LEARNING = load_learning()


def test_every_skill_has_a_category_and_a_tip():
    for skill in load_skills():
        entry = LEARNING.get(skill)
        assert entry, "no learning entry for %s" % skill
        assert entry["category"].strip(), skill
        assert len(entry["tip"]) > 20, skill


def test_category_of_a_known_skill():
    assert category_of("Docker", LEARNING) == "Cloud and DevOps"


def test_unknown_skill_falls_back_to_defaults():
    assert category_of("Quantum Basketweaving", LEARNING) == DEFAULT_CATEGORY
    assert learning_tip("Quantum Basketweaving", LEARNING)[0] == DEFAULT_TIP


def test_search_link_is_encoded():
    assert learning_tip("Quantum Basketweaving", LEARNING)[1] == \
        "https://www.google.com/search?q=learn+Quantum+Basketweaving+for+beginners"
    assert learning_tip("C++", LEARNING)[1].endswith("learn+C%2B%2B+for+beginners")
    assert learning_tip("CI/CD", LEARNING)[1].endswith("learn+CI%2FCD+for+beginners")


def test_coverage_counts_per_category():
    coverage = coverage_by_category(["Python", "Java", "MySQL"], ["Docker", "AWS", "Git"], LEARNING)
    assert coverage == {
        "Languages": {"Matched": 2, "Missing": 0},
        "Databases": {"Matched": 1, "Missing": 0},
        "Cloud and DevOps": {"Matched": 0, "Missing": 3},
    }


def test_coverage_of_nothing_is_empty():
    assert coverage_by_category([], [], LEARNING) == {}
