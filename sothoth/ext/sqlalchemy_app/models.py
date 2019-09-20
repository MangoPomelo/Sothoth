from sqlalchemy import Table, Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declared_attr, declarative_base

from ...elements import EntityMixin, RelationshipMixin, StatementMixin, TripleMixin
from ... import constants

class ModelBase(object):
    """
    An augmented base class for SqlAlchemy models.
    """

    @declared_attr
    def __tablename__(cls):
        """
        Return the lowercase class name as the name of the table.
        """
        return cls.__name__.lower()

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )


Base = declarative_base(cls=ModelBase)


class Entity(Base, EntityMixin):
    """
    An entity represents a coressponding entity
    reference in Knowledge Graph.
    """

    __tablename__ = 'entities'
    __table_args__ = (
        UniqueConstraint('type', 'name'),
    )

    name = Column(
        String(constants.ATTR_MAX_LENGTH),
        nullable=False
    )

    type = Column(
        String(constants.ATTR_MAX_LENGTH)
    )




class Statement(Base, StatementMixin):
    """
    A statement represents a single spoken unit, sentence or
    phase, which is regard as a context indicating a specified
    relationship.
    """

    __tablename__ = 'statements'
    __table_args__ = (
        UniqueConstraint('text', 'relationship_id'),
    )

    text = Column(
        String(constants.STATEMENT_TEXT_MAX_LENGTH),
        nullable=False
    )

    relationship_id = Column(
        Integer,
        ForeignKey('relationships.id'),
        nullable = False
    )


class Relationship(Base, RelationshipMixin):
    """
    A relationship represents a coressponding relationship
    reference in Knowledge Graph.
    """

    __tablename__ = 'relationships'
    __table_args__ = (
        UniqueConstraint('type', 'subject_type', 'object_type'),
    )

    type = Column(
        String(constants.ATTR_MAX_LENGTH),
        nullable = False
    )

    contexts = relationship(
        "Statement",
        cascade="all,delete"
    )

    subject_type = Column(
        String(constants.ATTR_MAX_LENGTH)
    )

    object_type = Column(
        String(constants.ATTR_MAX_LENGTH)
    )

    def get_contexts(self):
        """
        Return a list of contexts for this relationship.
        """
        return self.contexts

    def add_contexts(self, *contexts):
        """
        Add a list of strings to the relationship as contexts.
        """
        self.contexts.extend([
            Statement(text = context) for context in contexts
        ])


class Triple(Base, TripleMixin):
    """
    This class has shared methods used to
    normalize different triple models.
    """

    __tablename__ = 'triples'
    __table_args__ = (
        UniqueConstraint('subject_id', 'predicate_id', 'object_id'),
    )

    subject_id = Column(
        Integer,
        ForeignKey('entities.id'),
        nullable = False
    )

    predicate_id = Column(
        Integer,
        ForeignKey('relationships.id'),
        nullable = False
    )

    object_id = Column(
        Integer,
        ForeignKey('entities.id'),
        nullable = False
    )

    subject = relationship(
        'Entity',
        foreign_keys=[subject_id],
        backref = backref("related_triples_as_sub", cascade="all,delete")
    )

    predicate = relationship(
        'Relationship',
        backref = backref("related_triples_as_rel", cascade="all,delete")
    )

    object = relationship(
        'Entity',
        foreign_keys=[object_id],
        backref = backref("related_triples_as_obj", cascade="all,delete")
    )