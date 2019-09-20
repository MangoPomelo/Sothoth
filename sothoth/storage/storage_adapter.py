import logging


class StorageAdapter(object):
    """
    This is an abstract class that represents the interface
    that all storage adapters should implement.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize common attributes shared by all storage adapters.
        """
        self.logger = kwargs.get('logger', logging.getLogger(__name__))

    def get_model(self, model_name):
        """
        Return the model class for a given model name.

        model_name is case insensitive.
        """
        get_model_method = getattr(self, 'get_%s_model' % (
            model_name.lower(),
        ))

        return get_model_method()

    def get_object(self, object_name):
        """
        Return the class for a given object name.

        object_name is case insensitive.
        """
        get_object_method = getattr(self, 'get_%s_object' % (
            object_name.lower(),
        ))

        return get_object_method()

    def get_entity_object(self):
        from ..elements.entity import Entity
        return Entity

    def get_relationship_object(self):
        from ..elements.relationship import Relationship
        return Relationship

    def get_statement_object(self):
        from ..elements.statement import Statement
        return Statement

    def get_triple_object(self):
        from ..elements.triple import Triple
        return Triple

    def remove(self, element):
        """
        Removes the element(entity/relationship/statment/triple) that matches 
        the given element object and relatives. 
        Removes every fuzzy matched items if only given insufficient arguments.
        """
        raise self.AdapterMethodNotImplementedError(
            'The `remove` method is not implemented by this adapter.'
        )

    def get_candidate_triples(self, entity):
        """
        Return a list of triples like <entity.type, ?, ?> and <?, ?, entity.type>,
        If entity.type is not existed,then return <entity, ?, ?> and <?, ?, entity>.
        """
        raise self.AdapterMethodNotImplementedError(
            'The `get_candidate_triples` method is not implemented by this adapter.'
        )

    def create(self, triple):
        """
        Create a triple given an Triple object.
        Return the created triple.
        """
        raise self.AdapterMethodNotImplementedError(
            'The `create` method is not implemented by this adapter.'
        )

    def select(self, element):
        """
        Returns a list of objects that matches the given element object.
        """
        raise self.AdapterMethodNotImplementedError(
            'The `select` method is not implemented by this adapter.'
        )

    def update(self, element):
        """
        Modifies an entry in the database.
        Creates an entry if one does not exist.
        """
        raise self.AdapterMethodNotImplementedError(
            'The `update` method is not implemented by this adapter.'
        )

    def drop(self):
        """
        Drop the database attached to a given adapter.
        """
        raise self.AdapterMethodNotImplementedError(
            'The `drop` method is not implemented by this adapter.'
        )

    class EmptyDatabaseException(Exception):

        def __init__(self, message=None):
            default = 'The database currently contains no entries. At least one entry is expected.'
            super().__init__(message or default)

    class AdapterMethodNotImplementedError(NotImplementedError):
        """
        An exception to be raised when a storage adapter method has not been implemented.
        Typically this indicates that the method should be implement in a subclass.
        """
        pass