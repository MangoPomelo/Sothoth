"""
This module contains various word-comparison algorithms
designed to compare one word to another.
"""

class WordComparator:

    def __call__(self, word_a, word_b):
        return self.compare(word_a, word_b)

    def compare(self, word_a, word_b):
        return 0


class LevenshteinSimilarity(WordComparator):
    """
    Compare two words based on the Levenshtein distance
    of each word.
    """
    def __init__(self, **kwargs):
        # Use python-Levenshtein if available
        try:
            from Levenshtein.StringMatcher import StringMatcher as SequenceMatcher
        except ImportError:
            from difflib import SequenceMatcher

        self.sequence_matcher = SequenceMatcher

    def compare(self, word, other_word):
        """
        Compare the two input words.

        :return: The percent of similarity between the words.
        :rtype: float
        """

        # Return 0 if either word has a falsy word value
        if not word or not other_word:
            return 0

        # Get the lowercase version of both strings
        word = str(word.lower())
        other_word = str(other_word.lower())

        similarity = self.sequence_matcher(
            None,
            word,
            other_word
        )

        # Calculate a decimal percent of the similarity
        percent = round(similarity.ratio(), 2)

        return percent