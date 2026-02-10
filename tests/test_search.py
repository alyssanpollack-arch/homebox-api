import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import MagicMock
from search import fuzzy_search


def _make_item(name: str, location: str, category: str = "Other") -> MagicMock:
    item = MagicMock()
    item.name = name
    item.location = location
    item.category = category
    return item


class TestFuzzySearch:
    def test_exact_name_match(self):
        items = [_make_item("drill", "garage")]
        results = fuzzy_search(items, "drill")
        assert len(results) == 1
        assert results[0][1] == 100

    def test_partial_match(self):
        items = [_make_item("band-aids", "bathroom cabinet")]
        results = fuzzy_search(items, "bandaid")
        assert len(results) == 1
        assert results[0][1] >= 60

    def test_location_search(self):
        items = [
            _make_item("drill", "garage"),
            _make_item("hammer", "garage"),
            _make_item("plates", "kitchen"),
        ]
        results = fuzzy_search(items, "garage")
        assert len(results) == 2
        assert all(r[0].location == "garage" for r in results)

    def test_no_match_below_threshold(self):
        items = [_make_item("drill", "garage")]
        results = fuzzy_search(items, "xylophone")
        assert len(results) == 0

    def test_sorted_by_score(self):
        items = [
            _make_item("screwdriver", "garage"),
            _make_item("drill", "garage"),
        ]
        results = fuzzy_search(items, "drill")
        assert results[0][0].name == "drill"
        assert results[0][1] > results[1][1] if len(results) > 1 else True

    def test_category_search(self):
        items = [_make_item("hammer", "shed", "Tools")]
        results = fuzzy_search(items, "tools")
        assert len(results) == 1

    def test_empty_list(self):
        assert fuzzy_search([], "drill") == []

    def test_word_order_tolerance(self):
        items = [_make_item("power drill set", "garage")]
        results = fuzzy_search(items, "drill power")
        assert len(results) == 1
        assert results[0][1] >= 80
