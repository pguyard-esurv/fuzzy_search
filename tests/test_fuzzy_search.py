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
    assert ("Example 2", 100) not in results  # will not match
    assert (
        "This is an example",
        100,
    ) not in results  # Likely won't match with `ratio()`

    # Using `fuzz.partial_ratio()`
    results = fuzzy_search("Example", phrases, threshold=80, use_partial_ratio=True)
    assert ("Example 2", 100) in results  # Now will match
    assert ("This is an example", 100) in results  # Now should also match


def test_edge_cases():
    """Test edge cases like empty strings and low similarity."""
    phrases = ["Hello World", "Python Testing"]

    # Empty query should return no matches
    assert fuzzy_search("", phrases) == []

    # Very different query should return no matches
    assert fuzzy_search("abcdef", phrases, threshold=90) == []


def test_numbers_are_preserved():
    """Ensure numbers are NOT removed during preprocessing."""
    assert preprocess_text("Test 123") == "test 123"
    assert preprocess_text("Room 42 is open") == "room 42 is open"
    assert preprocess_text("1,000 people attended") == "1,000 people attended"


def test_should_ignore_match():
    """Test if certain phrase pairs are correctly ignored."""
    # Example 1 vs Example 2 should be ignored
    assert should_ignore_match("Example 1", "Example 2") is True
    assert should_ignore_match("example 1", "example 2") is True  # Case-insensitive

    # Test Case 1 vs Test Case 2 should be ignored
    assert should_ignore_match("Test Case 1", "Test Case 2") is True

    # These should NOT be ignored
    assert should_ignore_match("Example 1", "This is an example") is False
    assert should_ignore_match("Test Case 1", "Different Case") is False


def test_fuzzy_search_ignores_combinations():
    """Ensure fuzzy search does not return ignored phrase pairs."""
    phrases = [
        "Example 1",
        "Example 2",
        "This is an example",
        "Test Case 1",
        "Test Case 2",
    ]

    # Searching for "Example 1" should NOT return "Example 2"
    results = fuzzy_search("Example 1", phrases, threshold=80)
    print(results)
    assert ("Example 2", 100) not in results  # Should be ignored
    assert ("Example 1", 100) in results  # Should be ignored
    assert ("This is an example", 100) not in results  # Should be included
    results = fuzzy_search("Example", phrases, threshold=100, use_partial_ratio=True)
    assert (
        "This is an example",
        100,
    ) in results  # Should be included with partial ratio

    # Searching for "Test Case 1" should NOT return "Test Case 2"
    results = fuzzy_search("Test Case 1", phrases, threshold=80)
    assert ("Test Case 2", 100) not in results  # Should be ignored


def test_fuzzy_search_allows_numbers():
    """Ensure fuzzy search still allows matches when numbers are present."""
    phrases = ["Room 101", "Room 102", "Lecture Hall 200", "Welcome to section 300"]

    # Searching for "Room 101" should return an exact match
    results = fuzzy_search("Room 101", phrases, threshold=80)
    assert ("Room 101", 100) in results  # Should be included

    # Searching for "Lecture 200" should match "Lecture Hall 200" with a score ≥ 80
    results = fuzzy_search("Lecture 200", phrases, threshold=80, use_partial_ratio=True)

    # Extract the actual score
    match_score = next(
        (score for match, score in results if match == "Lecture Hall 200"), 0
    )

    assert match_score >= 80  # Allow partial matches with a high score


if __name__ == "__main__":
    pytest.main()
