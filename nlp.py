import re

FILLER_WORDS = re.compile(
    r"\b(um|uh|like|so|well|okay|oh|actually|basically|i think|you know)\b",
    re.IGNORECASE,
)

LEADING_ARTICLES = re.compile(r"^(the|a|an|my|our|some)\s+", re.IGNORECASE)

# Patterns tried in order — first match wins.
# Each returns (item, location) from the match groups.
PATTERNS: list[tuple[re.Pattern, tuple[int, int]]] = [
    # "X is/are in/on/under/behind/at Y"
    (re.compile(r"^(.+?)\s+(?:is|are)\s+(?:in|on|under|behind|at|inside|next to)\s+(.+)$", re.IGNORECASE), (1, 2)),
    # "[I/we] put/stored/left/placed/keep X in/on/under Y
    (re.compile(r"^(?:i|we)?\s*(?:put|stored|left|placed|keep|kept)\s+(.+?)\s+(?:in|on|under|behind|at|inside|next to)\s+(.+)$", re.IGNORECASE), (1, 2)),
    # "X, Y" (comma fallback)
    (re.compile(r"^(.+?)\s*,\s*(.+)$"), (1, 2)),
    # "X in/on/under Y" (bare preposition)
    (re.compile(r"^(.+?)\s+(?:in|on|under|behind|at|inside|next to)\s+(.+)$", re.IGNORECASE), (1, 2)),
    # "Y has/contains X" (inverted — swap groups)
    (re.compile(r"^(.+?)\s+(?:has|contains|holds)\s+(.+)$", re.IGNORECASE), (2, 1)),
]


def _clean(text: str) -> str:
    """Pre-process raw dictated text."""
    text = text.strip()
    # Strip trailing punctuation
    text = re.sub(r"[.!?]+$", "", text)
    # Remove filler words
    text = FILLER_WORDS.sub("", text)
    # Collapse whitespace
    text = re.sub(r"\s{2,}", " ", text).strip()
    return text


def _strip_articles(text: str) -> str:
    """Remove leading articles from a parsed fragment."""
    return LEADING_ARTICLES.sub("", text).strip()


def parse(raw_input: str) -> tuple[str, str] | None:
    """Parse natural language into (item, location). Returns None on failure."""
    cleaned = _clean(raw_input)
    if not cleaned:
        return None

    for pattern, (item_group, loc_group) in PATTERNS:
        m = pattern.match(cleaned)
        if m:
            item = _strip_articles(m.group(item_group).strip())
            location = _strip_articles(m.group(loc_group).strip())
            if item and location:
                return item, location

    return None
