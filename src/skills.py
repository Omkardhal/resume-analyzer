import json
import re
from pathlib import Path

from src.extract import clean_text

SKILLS_FILE = Path(__file__).resolve().parent.parent / "data" / "skills.json"


def load_skills(path=SKILLS_FILE):
    """Read skills.json and build one search pattern per skill.

    Each skill (and its aliases) goes through clean_text(), the same cleaning the
    resume text gets, so "CI/CD" becomes "ci cd" and both sides match.
    """
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    patterns = {}
    for skill, aliases in raw.items():
        variants = {clean_text(skill)} | {clean_text(a) for a in aliases}
        # longest first, so "spring boot" is tried before anything shorter
        options = "|".join(re.escape(v) for v in sorted(variants, key=len, reverse=True))
        patterns[skill] = re.compile(
            r"(?<![a-z0-9+#.])"            # not in the middle of a bigger word, e.g. "my" + "sql"
            r"(?:" + options + r")"
            r"(?![a-z0-9+#]|\.[a-z0-9])"   # not followed by more letters, "+" or "#", or ".js"
        )
    return patterns


def find_skills(text, patterns):
    """Return the set of skills that appear in text (text must already be cleaned)."""
    return {skill for skill, pattern in patterns.items() if pattern.search(text)}
