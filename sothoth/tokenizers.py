"""
Text tokenizers.
"""


class Tokenizer(object):
    """
    A processing interface for tokenizing a string.
    Subclasses must define ``tokenize()``
    """
    def __call__(self, text):
        return self.tokenize(text)
        
    def tokenize(self, text):
        """
        Return a list of tokenized substrings.

        :param text: A single string.
        :returns: A list of tokenized substrings.
        :rtype list(str)
        """
        raise self.TokenizerMethodNotImplementedError(
            'The `tokenize` method is not implemented by this tokenizer.'
        )

    class TokenizerMethodNotImplementedError(NotImplementedError):
        """
        An exception to be raised when a tokenizer method has not been implemented.
        Typically this indicates that the method should be implement in a subclass.
        """
        pass

class TreebankTokenizer(Tokenizer):
	"""
	Treebank word tokenizer from nltk module.
	"""
	def __init__(self, **kwargs):
		import nltk
		self.treebank_tokenize = nltk.word_tokenize

	def tokenize(self, text):
		return self.treebank_tokenize(text)