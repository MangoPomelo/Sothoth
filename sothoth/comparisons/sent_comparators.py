"""
This module contains various sentence-comparison algorithms
designed to compare one sentence to another.
"""


class SentComparator:

    def __call__(self, sentence_a, sentence_b):
        return self.compare(sentence_a, sentence_b)

    def compare(self, sentence_a, sentence_b):
        return 0


class LevenshteinSimilarity(SentComparator):
    """
    Compare two sentences based on the Levenshtein distance
    of each sentence.

    For example, there is a 65% similarity between the sentences
    "where is the post office?" and "looking for the post office"
    based on the Levenshtein distance algorithm.
    """
    def __init__(self, **kwargs):
        # Use python-Levenshtein if available
        try:
            from Levenshtein.StringMatcher import StringMatcher as SequenceMatcher
        except ImportError:
            from difflib import SequenceMatcher

        self.sequence_matcher = SequenceMatcher

    def compare(self, sentence, other_sentence):
        """
        Compare the two input sentences.

        :return: The percent of similarity between the sentences.
        :rtype: float
        """

        # Return 0 if either sentence has a falsy sentence value
        if not sentence or not other_sentence:
            return 0

        # Get the lowercase version of both strings
        sentence = str(sentence.lower())
        other_sentence = str(other_sentence.lower())

        similarity = self.sequence_matcher(
            None,
            sentence,
            other_sentence
        )

        # Calculate a decimal percent of the similarity
        percent = round(similarity.ratio(), 2)

        return percent

class JaccardSimilarity(SentComparator):
    """
    Calculates the similarity of two sentences based on the Jaccard index.
    The Jaccard index is composed of a numerator and denominator.
    In the numerator, we count the number of items that are shared between the sets.
    In the denominator, we count the total number of items across both sets.
    Let's say we define sentences to be equivalent if 50% or more of their tokens are equivalent.
    Here are two sample sentences:
        The young cat is hungry.
        The cat is very hungry.
    When we parse these sentences to remove stopwords, we end up with the following two sets:
        {young, cat, hungry}
        {cat, very, hungry}
    In our example above, our intersection is {cat, hungry}, which has count of two.
    The union of the sets is {young, cat, very, hungry}, which has a count of four.
    Therefore, our `Jaccard similarity index`_ is two divided by four, or 50%.
    Given our similarity threshold above, we would consider this to be a match.
    .. _`Jaccard similarity index`: https://en.wikipedia.org/wiki/Jaccard_index
    """
    def __init__(self, **kwargs):
    	from .. import utils
    	tokenizer = kwargs.get('tokenizer', 'sothoth.tokenizers.TreebankTokenizer')

    	self.tokenizer = utils.initialize_class(tokenizer, **kwargs)

    def compare(self, sentence, other_sentence):
    	# Tokenize the sentences
    	tokenized_sentence, other_tokenized_sentence = (
    		self.tokenizer(sentence), self.tokenizer(other_sentence)
    	)

    	set_a, set_b = set(tokenized_sentence), set(other_tokenized_sentence)

    	# Calculate Jaccard similarity
    	numerator = len(set_a.intersection(set_b))
    	denominator = float(len(set_a.union(set_b)))
    	ratio = numerator / denominator

    	return ratio


class CosineSimilarity(SentComparator):
    """
    Calculates the similarity of two sentences based on Consine similarity 
    using scipy module.

    Warning:
    The vocabulary is the union of two sentences.

    In this way, there would be uncomparable situations when other pair of 
    sentences has a diffent size of vocabulary.
    
    So we highly recommand you customize your own cosine similarity with global vocabulary
    """
    def __init__(self, **kwargs):
        from .. import utils
        tokenizer = kwargs.get('tokenizer', 'sothoth.tokenizers.TreebankTokenizer')

        self.tokenizer = utils.initialize_class(tokenizer, **kwargs)

    def compare(self, sentence, other_sentence):
        from scipy import spatial

        # Tokenize the sentences
        tokenized_sentence, other_tokenized_sentence = (
            self.tokenizer(sentence), self.tokenizer(other_sentence)
        )

        counter = dict()

        # Count token in sentence A
        for token in tokenized_sentence:
            token_count = list(counter.get(token, (0, 0)))
            token_count[0] += 1
            counter[token] = tuple(token_count)

        # Count token in sentence B
        for token in other_tokenized_sentence:
            token_count = list(counter.get(token, (0, 0)))
            token_count[1] += 1
            counter[token] = tuple(token_count)

        # Allocate zero vectors
        vec_a, vec_b = [0 for _ in range(len(counter))], [0 for _ in range(len(counter))]

        for idx, (token, (count_in_a, count_in_b)) in enumerate(counter.items()):
            vec_a[idx] = count_in_a
            vec_b[idx] = count_in_b

        similarity = 1 - spatial.distance.cosine(vec_a, vec_b)

        return similarity