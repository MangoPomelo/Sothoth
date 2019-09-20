import logging
from . import utils


class Answeroid(object):
    """
    A knowledge based question-answer chat bot.
    """
    def __init__(self, **kwargs):
        # Configure storage
        storage_adapter = kwargs.get('storage_adapter', 'sothoth.storage.SQLStorageAdapter')

        self.storage = utils.initialize_class(storage_adapter)

        # Configure preprocessing functions
        preprocessors = kwargs.get(
            'preprocessors', [
                'sothoth.preprocessors.clean_whitespace',
            ]
        )

        self.preprocessors = []

        for preprocessor in preprocessors:
            self.preprocessors.append(utils.import_module(preprocessor))

        # Configure word tokenizer
        tokenizer = kwargs.get('tokenizer', 'sothoth.tokenizers.TreebankTokenizer')

        self.tokenizer = utils.initialize_class(tokenizer, **kwargs)

        # Configure pos tagger
        tagger = kwargs.get('tagger', 'sothoth.taggers.PerceptronTagger')

        self.tagger = utils.initialize_class(tagger, **kwargs)

        # Configure NE recognizer
        recognizer = kwargs.get(
            'recognizer', 'sothoth.recognizers.MaximumEntropyRecognizer'
        )

        self.recognizer = utils.initialize_class(recognizer, **kwargs)

        # Configure word comparator to measure distance between 
        # two entities` name and two entities` type
        word_comparator = kwargs.get(
            'word_comparator', 'sothoth.comparisons.word_comparators.LevenshteinSimilarity'
        )

        self.word_comparator = utils.initialize_class(word_comparator, **kwargs)

        # Configure sentence comparator to measure distance between
        # two statements` text
        sent_comparator = kwargs.get(
            'sent_comparator', 'sothoth.comparisons.sent_comparators.LevenshteinSimilarity'
        )

        self.sent_comparator = utils.initialize_class(sent_comparator, **kwargs)

        # Configure logger
        self.logger = kwargs.get('logger', logging.getLogger(__name__))

    def learn_knowledge(self, knowledge):
        """
        Feed provided valid triple(s) to the storage.

        :param knowledge: A list of triples or a single triple.
        :returns: A list wrapped triple(s) which was provided.
        :rtype: list(Triple) 
        """
        Triple = self.storage.get_object('triple')

        # Wrap if a single triple
        if isinstance(knowledge, Triple):
            knowledge = [knowledge]

        if isinstance(knowledge, list):
            # Check if every entry is a Triple
            for each_triple in knowledge:
                if not isinstance(each_triple, Triple):
                    raise self.AnsweroidException(
                        'Input should be single or multiple triple objects.'
                        'Illegal object was provided'
                    )

            # Save the triple(s) to the storage
            for each_triple in knowledge:
                self.storage.create(each_triple)

                self.logger.info("Adding '{}' to the storage".format(repr(each_triple)))

        else:
            raise self.AnsweroidException(
                'Either a triple object or a list of triples is required.'
                'Neither was provided'
            )

        return knowledge

    def get_answer(self, question=None, **kwargs):
        """
        Return the response based on the input.

        :param statement: A question string.
        :returns: An answer or answers to the input.
        :rtype: set(str)
        """

        if isinstance(question, str) and question:
            kwargs['text'] = question
        else:
            raise self.AnsweroidException(
                'A not null string object should be provided.'
            )

        input_question = kwargs.pop('text')

        # Preprocess the input question
        for preprocessor in self.preprocessors:
            input_question = preprocessor(input_question)

        # Tokenize the input question
        input_question = self.tokenizer(input_question)

        # Tag the input question
        input_question = self.tagger(input_question)

        # Pick out named entities
        input_question = self.recognizer(input_question)

        contained_entities = [item for item in input_question if item[-1] != '<>']

        # Pick out all storaged entities for scoring
        Entity = self.storage.get_object('entity')
        all_entities = self.storage.select(Entity())

        
        import itertools
        linking_entities = []
        # Score every mentioned entity and record every best match in linking_entities
        for entity_name, _, entity_type in contained_entities:
            best_match = None
            best_match_score = -1.0

            all_entities, copied_iterator = itertools.tee(all_entities)

            mentioned_entity = Entity(name = entity_name, type = entity_type)

            for entity in copied_iterator:
                name_score = self.word_comparator(entity.name, mentioned_entity.name)
                type_score = self.word_comparator(entity.type, mentioned_entity.type)
                average_score = (name_score + type_score) / 2

                if average_score > best_match_score:
                    best_match = entity
                    best_match_score = average_score
            linking_entities.append(best_match)

        # Transform from Model to Object
        linking_entities = [self.storage.model_to_object(entity) for entity in linking_entities]

        if not linking_entities:
            self.logger.warn(
                'No entity has been recognized.'
            )

        # Construct hollow statement
        hollow_text = []
        for token, pos_tag, entity_type in input_question:
            if entity_type == '<>':
                hollow_text.append(token)
            else:
                hollow_text.append(entity_type)
        hollow_text = ' '.join(hollow_text)

        Statement = self.storage.get_object('statement')
        holding_statement = Statement(text = hollow_text)

        responsing_answers = []
        # Find the best candidate triple for each linked entity
        # Meanwhile, record responsing answers
        for entity in linking_entities:
            best_match = None
            best_match_score = -1.0
            
            candidate_triples = self.storage.get_candidate_triples(entity)
            
            for triple in candidate_triples:
                statements = triple.predicate.contexts

                triple_max_score = max(
                    self.sent_comparator(statement.text, holding_statement.text) 
                    for statement in statements
                )

                if triple_max_score > best_match_score:
                    best_match = triple
                    best_match_score = triple_max_score
                self.logger.info('For {}, the {}`s max score is {:.2f}'.format(repr(entity), repr(triple), triple_max_score))

            if entity.id == best_match.subject.id:
                # This entity is subject, therefore, record the object`s name as the answer
                responsing_answers.append(best_match.object.name)
            else:
                responsing_answers.append(best_match.subject.name)

        return set(responsing_answers)

    class AnsweroidException(Exception):
        pass