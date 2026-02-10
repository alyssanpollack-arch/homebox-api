import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from categories import categorize


def test_tools():
    assert categorize("screwdriver") == "Tools"
    assert categorize("power drill") == "Tools"
    assert categorize("hammer") == "Tools"


def test_kitchen():
    assert categorize("frying pan") == "Kitchen"
    assert categorize("cutting board") == "Kitchen"


def test_medical():
    assert categorize("band-aids") == "Medical"
    assert categorize("thermometer") == "Medical"


def test_cleaning():
    assert categorize("vacuum cleaner") == "Cleaning"
    assert categorize("dish soap") == "Cleaning"


def test_electronics():
    assert categorize("phone charger") == "Electronics"
    assert categorize("usb cable") == "Electronics"


def test_seasonal():
    assert categorize("christmas ornaments") == "Seasonal"


def test_kids():
    assert categorize("lego set") == "Kids"
    assert categorize("stuffed animal") == "Kids"


def test_outdoor():
    assert categorize("garden hose") == "Outdoor"


def test_clothing():
    assert categorize("winter jacket") == "Clothing"
    assert categorize("running shoes") == "Clothing"


def test_other():
    assert categorize("random thing") == "Other"
    assert categorize("widget") == "Other"
