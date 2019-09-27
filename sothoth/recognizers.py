"""
Named entity recognizers.
"""


class Recognizer(object):
    """
    A processing interface for assigning a named entity tag to each (token, tag) pair in a list.
    Subclasses must define ``distinct()``
    """
    def __call__(self, tagged_tokens):
        return self.distinct(tagged_tokens)

    def distinct(self, tagged_tokens):
        """
        Detect entity for the given tagged tokens sequence, and return a 
        list of NER tagged tuples.  A tagged tuple is encoded as a 
        tuple ``(entity, pos tag, '<entity_type>') or (token, pos tag, '<>')``.

        :param tokens: A list of tagged tokens.
        :returns: A list of (entity, pos_tag, entity_type) pairs.
        :rtype list(tuple(str, str, str))
        """
        raise self.RecognizerMethodNotImplementedError(
            'The `tag` method is not implemented by this recognizer.'
        )

    class RecognizerMethodNotImplementedError(NotImplementedError):
        """
        An exception to be raised when a tagger method has not been implemented.
        Typically this indicates that the method should be implement in a subclass.
        """
        pass

class MaximumEntropyRecognizer(Recognizer):
    """
    Maximum entropy named entity recognizer from nltk module.
    """
    def __init__(self, **kwargs):
        import nltk
        self.maxent_distinct = nltk.ne_chunk

    def distinct(self, tagged_tokens):
        import nltk.tree
        from collections import Counter
        result_tree = self.maxent_distinct(tagged_tokens)
        
        # Format the result
        result_list = []
        for item in result_tree:
            if isinstance(item, nltk.tree.Tree):
                # This tuple has been distinct as a named entity
                
                entity_type = item.label()

                # Join the tokens to be an entity if it`s a phrase
                entity = ' '.join(token for token, pos_tag in item)

                # Get the most common pos tag as the entity pas tag
                counter = Counter()
                for _, pos_tag in item:
                    counter[pos_tag] += 1
                most_common_tag, times = counter.most_common(1)[0]

                result_list.append((entity, most_common_tag, '<%s>' % entity_type))

            else:
                result_list.append((item[0], item[1], '<>'))

        return result_list
