import json
from pathlib import Path
from urllib.parse import quote_plus

LEARNING_FILE = Path(__file__).resolve().parent.parent / "data" / "learning.json"

# Used for any skill you add to skills.json but have not added to learning.json yet.
DEFAULT_CATEGORY = "Other"
DEFAULT_TIP = "Find a beginner tutorial and build one small project with it."


def load_learning(path=LEARNING_FILE):
    """Read learning.json: a category and a learning tip for each skill."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def category_of(skill, learning):
    return learning.get(skill, {}).get("category", DEFAULT_CATEGORY)


def learning_tip(skill, learning):
    """Return (tip, link) for a skill. The link is a web search for beginner tutorials."""
    tip = learning.get(skill, {}).get("tip", DEFAULT_TIP)
    link = "https://www.google.com/search?q=" + quote_plus("learn " + skill + " for beginners")
    return tip, link


def coverage_by_category(matched, missing, learning):
    """Count matched and missing skills per category.

    Only categories that the job asks for appear in the result, e.g.
    {"Databases": {"Matched": 3, "Missing": 1}, "Cloud and DevOps": {"Matched": 0, "Missing": 2}}
    """
    counts = {}
    for skill in matched:
        entry = counts.setdefault(category_of(skill, learning), {"Matched": 0, "Missing": 0})
        entry["Matched"] += 1
    for skill in missing:
        entry = counts.setdefault(category_of(skill, learning), {"Matched": 0, "Missing": 0})
        entry["Missing"] += 1
    return counts
