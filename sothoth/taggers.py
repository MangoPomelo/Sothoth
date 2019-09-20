"""
Text pos taggers.
"""


class Tagger(object):
    """
    A processing interface for assigning a tag to each token in a list.
    Subclasses must define ``tag()``
    """
    def __call__(self, tokens):
        return self.tag(tokens)

    def tag(self, tokens):
        """
        Determine the most appropriate tag sequence for the given
        token sequence, and return a corresponding list of tagged
        tokens.  A tagged token is encoded as a tuple ``(token, tag)``.

        :param tokens: A list of tokens.
        :returns: A list of (token, tag) pairs.
        :rtype list(tuple(str, str))
        """
        raise self.TaggerMethodNotImplementedError(
            'The `tag` method is not implemented by this tagger.'
        )

    class TaggerMethodNotImplementedError(NotImplementedError):
        """
        An exception to be raised when a tagger method has not been implemented.
        Typically this indicates that the method should be implement in a subclass.
        """
        pass

class PerceptronTagger(Tagger):
	"""
	Perceptron tagger from nltk module.
	"""
	def __init__(self, **kwargs):
		import nltk
		self.perceptron_tag = nltk.pos_tag

	def tag(self, tokens):
		return self.perceptron_tag(tokens)