import pytest

from ..fuzzy_search.fuzzy_search import (
    expand_abbreviations,
    fuzzy_search,
    preprocess_text,
    should_ignore_match,
)


def test_expand_abbreviations():
    """Test abbreviation expansion."""
    assert expand_abbreviations("Dr. Smith") == "Doctor Smith"
    assert expand_abbreviations("e.g. apples, oranges") == "for example apples, oranges"
    assert expand_abbreviations("etc.") == "et cetera"
    assert expand_abbreviations("Nothing to expand") == "Nothing to expand"


def test_preprocess_text():
    """Test text preprocessing, including abbreviation expansion and normalisation."""
    assert preprocess_text("Dr. Smith  ") == "doctor smith"
    assert preprocess_text("Example 1") == "example"
    assert preprocess_text("Example 2") == "example"
    assert preprocess_text("e.g. bananas") == "for example bananas"
    assert preprocess_text("Mixed  Case") == "mixed case"


def test_should_ignore_match():
    """Test if two phrases should be ignored as identical after preprocessing."""
    assert should_ignore_match("Example 1", "Example 2") is True  # Should be ignored
    assert (
        should_ignore_match("Example 1", "This is an example") is False
    )  # Different content
    assert should_ignore_match("Dr. Smith", "Doctor Smith") is True  # Treated as same
    assert (
        should_ignore_match("hello world", "Hello  World") is True
    )  # Case & spacing don't matter


def test_fuzzy_search():
    """Test fuzzy search matching with preprocessing and filtering."""
    phrases = [
        "Dr. Smith is a cardiologist",
        "Doctor Smith is a specialist",
        "Example 1",
        "Example 2",
        "This is an example",
    ]

    # Using standard `fuzz.ratio()`
    results = fuzzy_search("Example 1", phrases, threshold=80)
    assert ("Example 2", 100) not in results  # Should not match due to filtering
    assert (
        "This is an example",
        100,
    ) not in results  # Likely won't match with `ratio()`

    # Using `fuzz.partial_ratio()`
    results = fuzzy_search("Example 1", phrases, threshold=80, use_partial_ratio=True)
    assert ("Example 2", 100) not in results  # Still shouldn't match
    assert ("This is an example", 100) in results  # Now should match


def test_edge_cases():
    """Test edge cases like empty strings and low similarity."""
    phrases = ["Hello World", "Python Testing"]

    # Empty query should return no matches
    assert fuzzy_search("", phrases) == []

    # Very different query should return no matches
    assert fuzzy_search("abcdef", phrases, threshold=90) == []

    # Test numbers removal (optional, if we are removing numbers)
    assert preprocess_text("Test 123") == "test"


if __name__ == "__main__":
    pytest.main()
