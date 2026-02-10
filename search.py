from rapidfuzz import fuzz

from models import Item

THRESHOLD = 60


def fuzzy_search(items: list[Item], query: str) -> list[tuple[Item, int]]:
    """Search items by name, location, and category. Returns (item, score) pairs sorted by score."""
    results: list[tuple[Item, int]] = []

    for item in items:
        # Score against name, location, and category — take the best
        scores = [
            fuzz.token_set_ratio(query, item.name),
            fuzz.token_set_ratio(query, item.location),
            fuzz.token_set_ratio(query, item.category),
        ]
        best = int(max(scores))
        if best >= THRESHOLD:
            results.append((item, best))

    results.sort(key=lambda r: r[1], reverse=True)
    return results
