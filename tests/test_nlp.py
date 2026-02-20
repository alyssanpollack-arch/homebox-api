import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from nlp import parse


class TestIsArePattern:
    def test_basic(self):
        assert parse("the drill is in the garage toolbox") == ("drill", "garage toolbox")

    def test_are(self):
        assert parse("the towels are in the linen closet") == ("towels", "linen closet")

    def test_on(self):
        assert parse("the keys are on the kitchen counter") == ("keys", "kitchen counter")

    def test_under(self):
        assert parse("the spare key is under the doormat") == ("spare key", "doormat")


class TestPutStoredPattern:
    def test_i_put(self):
        assert parse("I put the drill in the garage") == ("drill", "garage")

    def test_stored(self):
        assert parse("I stored the winter coats in the attic") == ("winter coats", "attic")

    def test_we_left(self):
        assert parse("we left the stroller in the mudroom") == ("stroller", "mudroom")

    def test_no_pronoun(self):
        assert parse("put the batteries in the junk drawer") == ("batteries", "junk drawer")

    def test_im_putting(self):
        assert parse("I'm putting the superglue in the laundry room cabinet") == ("superglue", "laundry room cabinet")

    def test_im_storing(self):
        assert parse("I'm storing the blankets in the closet") == ("blankets", "closet")


class TestCommaFallback:
    def test_simple(self):
        assert parse("drill, garage") == ("drill", "garage")

    def test_multi_word(self):
        assert parse("band-aids, bathroom cabinet") == ("band-aids", "bathroom cabinet")


class TestBarePreposition:
    def test_in(self):
        assert parse("drill in garage") == ("drill", "garage")

    def test_on(self):
        assert parse("scissors on desk") == ("scissors", "desk")


class TestInvertedPattern:
    def test_has(self):
        assert parse("the garage has my power tools") == ("power tools", "garage")

    def test_contains(self):
        assert parse("the freezer contains ice cream") == ("ice cream", "freezer")


class TestPreprocessing:
    def test_trailing_period(self):
        assert parse("the drill is in the garage.") == ("drill", "garage")

    def test_filler_words(self):
        assert parse("um I think the drill is in the garage") == ("drill", "garage")

    def test_strips_articles(self):
        assert parse("my hammer is in our shed") == ("hammer", "shed")


class TestFailure:
    def test_empty(self):
        assert parse("") is None

    def test_no_match(self):
        assert parse("hello world") is None

    def test_whitespace(self):
        assert parse("   ") is None
