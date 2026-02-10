CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "Tools": [
        "drill", "hammer", "screw", "nail", "wrench", "plier", "saw",
        "tape measure", "level", "socket", "bolt", "nut", "clamp",
        "sandpaper", "toolbox", "allen", "hex key",
    ],
    "Kitchen": [
        "pan", "pot", "spatula", "whisk", "knife", "cutting board",
        "blender", "mixer", "plate", "bowl", "cup", "mug", "fork",
        "spoon", "ladle", "colander", "strainer", "baking", "oven mitt",
        "tupperware", "container", "food",
    ],
    "Medical": [
        "bandaid", "band-aid", "medicine", "pill", "vitamin", "thermometer",
        "first aid", "aspirin", "ibuprofen", "tylenol", "gauze", "antiseptic",
        "prescription", "inhaler", "epipen",
    ],
    "Cleaning": [
        "broom", "mop", "vacuum", "sponge", "bleach", "detergent",
        "soap", "wipe", "duster", "spray", "trash bag", "brush",
        "cleaner", "disinfect",
    ],
    "Electronics": [
        "charger", "cable", "battery", "adapter", "remote", "usb",
        "hdmi", "extension cord", "power strip", "headphone", "earbud",
        "speaker", "controller", "mouse", "keyboard",
    ],
    "Seasonal": [
        "christmas", "halloween", "easter", "holiday", "ornament",
        "decoration", "wreath", "lights", "costume", "pumpkin",
        "thanksgiving", "valentine",
    ],
    "Kids": [
        "toy", "lego", "doll", "crayon", "marker", "coloring",
        "puzzle", "game", "stuffed animal", "pacifier", "bottle",
        "diaper", "stroller", "car seat", "playmat",
    ],
    "Outdoor": [
        "garden", "hose", "shovel", "rake", "lawn", "seed",
        "fertilizer", "pot", "planter", "grill", "camping",
        "tent", "sleeping bag", "cooler", "bike", "helmet",
    ],
    "Clothing": [
        "shirt", "pants", "jacket", "coat", "shoe", "boot",
        "sock", "hat", "glove", "scarf", "sweater", "dress",
        "suit", "tie", "belt", "shorts",
    ],
}


def categorize(item_name: str) -> str:
    """Return a category for the item based on keyword substring matching."""
    lower = item_name.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in lower:
                return category
    return "Other"
