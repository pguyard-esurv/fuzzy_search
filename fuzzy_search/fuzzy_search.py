import logging
import re

from rapidfuzz import fuzz, process

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Define abbreviation expansions
ABBREVIATIONS = {
    "Dr.": "Doctor",
    "e.g.": "for example",
    "etc.": "et cetera",
    # "etc": "et cetera",
}

# List of patterns that should NOT be considered similar
IGNORE_COMBINATIONS = [
    (
        r"example 1",
        r"example 2",
    ),  # Ignore matches between "Example 1" and "Example 2"
    (r"test case \d+", r"test case \d+"),  # Ignore "Test Case 1" matching "Test Case 2"
]

# List of patterns that should NOT be considered similar
IGNORE_SIMILAR = [
    (
        r"developer \d+",
        "developer",
    ),  # "Example 1" and "Example 2" should be treated as "Example"
]


def expand_abbreviations(text: str) -> str:
    """
    Expands known abbreviations in the input text.
    Handles punctuation correctly by looking for abbreviations as standalone words.

    Args:
        text (str): The input text.

    Returns:
        str: Text with abbreviations expanded.
    """
    try:
        for abbr, full_form in ABBREVIATIONS.items():
            # Match abbreviation even if it has punctuation next to it (e.g., "Dr., " or "Dr!").
            pattern = rf"(?<!\w){re.escape(abbr)}(?!\w)"
            text = re.sub(pattern, full_form, text, flags=re.IGNORECASE)
        return text
    except Exception as e:
        logger.error(f"Error in expand_abbreviations: {e}")
        return text


def preprocess_text(text: str) -> str:
    """
    Expands abbreviations, removes numbers, converts to lowercase, and replaces ignored patterns.
    """
    try:
        text = expand_abbreviations(text)  # Expand abbreviations
        text = text.lower()  # Convert to lowercase
        for pattern, replacement in IGNORE_SIMILAR:
            text = re.sub(pattern, replacement, text)  # Replace ignored patterns
        text = re.sub(r"\s+", " ", text).strip()  # Normalize spaces
        return text
    except Exception as e:
        logger.error(f"Error in preprocess_text: {e}")
        return text


def should_ignore_match(text1: str, text2: str) -> bool:
    """
    Determines if a match should be ignored based on specific exclusions.

    Args:
        text1 (str): First text.
        text2 (str): Second text.

    Returns:
        bool: True if the match should be ignored, False otherwise.
    """
    try:
        processed1, processed2 = preprocess_text(text1), preprocess_text(text2)

        # Check if the combination of text1 and text2 should be ignored
        for pattern1, pattern2 in IGNORE_COMBINATIONS:
            if (
                re.fullmatch(pattern1, processed1)
                and re.fullmatch(pattern2, processed2)
            ) or (
                re.fullmatch(pattern2, processed1)
                and re.fullmatch(pattern1, processed2)
            ):
                logger.info(f"Ignoring match: '{text1}' <-> '{text2}'")
                return True

        return False
    except Exception as e:
        logger.error(f"Error in should_ignore_match: {e}")
        return False


def fuzzy_search(
    query: str, phrases: list, threshold: int = 80, use_partial_ratio: bool = False
) -> list:
    """
    Performs a fuzzy search on a list of phrases with pre-processing.

    Args:
        query (str): The search term.
        phrases (list): The list of phrases to search from.
        threshold (int, optional): Minimum similarity score. Defaults to 80.
        use_partial_ratio (bool, optional): Use `partial_ratio` for substring matches. Defaults to False.

    Returns:
        list: List of (phrase, score) tuples for matching phrases.
    """
    try:
        query_clean = preprocess_text(query)
        logger.info(f"Searching for: {query_clean}")

        # Preprocess phrases
        processed_phrases = {phrase: preprocess_text(phrase) for phrase in phrases}

        # Choose the similarity metric
        scorer = fuzz.partial_ratio if use_partial_ratio else fuzz.ratio

        # Perform fuzzy matching
        matches = process.extract(
            query_clean, processed_phrases.values(), scorer=scorer, limit=5
        )

        # Map back to original phrases and filter ignored matches
        results = []
        for orig, proc in processed_phrases.items():
            for match, score, _ in matches:
                if proc == match and score >= threshold:
                    if not should_ignore_match(
                        query, orig
                    ):  # Exclude unwanted combinations
                        results.append((orig, score))

        logger.info(
            f"Found {len(results)} matches for '{query}' using {'partial_ratio' if use_partial_ratio else 'ratio'}"
        )
        return sorted(results, key=lambda x: x[1], reverse=True)

    except Exception as e:
        logger.error(f"Error in fuzzy_search: {e}")
        return []


def main():
    """
    Demonstrates different fuzzy search cases with various test scenarios.
    """
    phrases = [
        "Dr. Smith is a cardiologist",
        "Doctor Smith is a specialist",
        "Example 1",
        "Example 2",
        "This is an example",
        "Python programming is fun",
        "Learn AI and ML",
        "Python Testing",
        "The quick brown fox jumps over the lazy dog",
        "123 Main Street",
    ]

    test_cases = [
        # Basic Matching
        ("Dr. Smith is a specialist", 80, False),
        ("Example 1", 80, False),
        ("Example 1", 80, True),  # Using partial_ratio
        ("Python", 80, False),
        # Handling abbreviations
        ("Doctor Smith is a cardiologist", 80, False),
        ("Doctor", 80, False),
        # Ignoring Example 1 vs Example 2
        ("Example 1", 80, False),
        ("Example 2", 80, False),
        # Edge Cases
        ("abcdef", 90, False),  # No similar match
        ("", 80, False),  # Empty input
        ("123 Main", 80, False),  # Numbers in query
    ]

    for query, threshold, use_partial in test_cases:
        print(f"\n🔍 Query: '{query}' (Threshold: {threshold}, Partial: {use_partial})")
        results = fuzzy_search(
            query, phrases, threshold=threshold, use_partial_ratio=use_partial
        )

        if results:
            for match, score in results:
                print(f" ✅ Match: '{match}' (Score: {score})")
        else:
            print(" ❌ No matches found.")


if __name__ == "__main__":
    main()
