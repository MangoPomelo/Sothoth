from . import StorageAdapter


class SQLStorageAdapter(StorageAdapter):
    """
    The SQLStorageAdapter allows ChatterBot to store conversation
    data in any database supported by the SQL Alchemy ORM.

    All parameters are optional, by default a sqlite database is used.

    It will check if tables are present, if they are not, it will attempt
    to create the required tables.

    :keyword database_uri: eg: sqlite:///database_test.db',
        The database_uri can be specified to choose database driver.
    :type database_uri: str
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        self.database_uri = kwargs.get('database_uri', False)

        # None results in a sqlite in-memory database as the default
        if self.database_uri is None:
            self.database_uri = 'sqlite://'

        # Create a file database if the database is not a connection string
        if not self.database_uri:
            self.database_uri = 'sqlite:///db.sqlite3'

        self.engine = create_engine(self.database_uri, convert_unicode=True)

        if self.database_uri.startswith('sqlite://'):
            from sqlalchemy.engine import Engine
            from sqlalchemy import event

            @event.listens_for(Engine, 'connect')
            def set_sqlite_pragma(dbapi_connection, connection_record):
                dbapi_connection.execute('PRAGMA journal_mode=WAL')
                dbapi_connection.execute('PRAGMA synchronous=NORMAL')

        if not self.engine.dialect.has_table(self.engine, 'Statement'):
            self.create_database()

        self.Session = sessionmaker(bind=self.engine, expire_on_commit=True)


    def get_entity_model(self):
        """
        Return the entity model.
        """
        from ..ext.sqlalchemy_app.models import Entity
        return Entity

    def get_relationship_model(self):
        """
        Return the relationship model.
        """
        from ..ext.sqlalchemy_app.models import Relationship
        return Relationship

    def get_statement_model(self):
        """
        Return the statement model.
        """
        from ..ext.sqlalchemy_app.models import Statement
        return Statement

    def get_triple_model(self):
        """
        Return the triple model.
        """
        from ..ext.sqlalchemy_app.models import Triple
        return Triple

    def get_object_name(self, object):
        return object.__class__.__name__

    def get_model_name(self, model):
        return model.__class__.__name__

    def model_to_object(self, model):
        from ..ext.sqlalchemy_app.models import Entity, Relationship, Statement, Triple

        serialization = model.serialize()

        if isinstance(model, Relationship) and model.contexts:
            # Deal with nested statements
            '''
            BUG: I don`t know what happened,when use similiar structure in 'object_to_model',
            there will be a bug by deepcopying statements, therefore, I use serialize() to
            avoid recursion evoking, hope someone can solve this.
            '''
            serialization['contexts'] = [self.model_to_object(context) for context in model.contexts]

            object = self.get_object(self.get_model_name(model))

            return object(**serialization) 
        
        elif isinstance(model, Triple) and (model.subject or model.predicate or model.object):
            # Deal with nested entities and relationship

            if model.subject: serialization['subject'] = self.model_to_object(model.subject)
            if model.predicate: serialization['predicate'] = self.model_to_object(model.predicate)
            if model.object: serialization['object'] = self.model_to_object(model.object)

            triple = self.get_object(self.get_model_name(model))

            return triple(**serialization)

        else:
            # Non-nested structure
            object = self.get_object(self.get_model_name(model))

            return object(**serialization)

    def object_to_model(self, object):
        from ..elements import Entity, Relationship, Statement, Triple

        serialization = object.serialize()

        if isinstance(object, Relationship) and object.contexts:
            # Deal with nested statements
            serialization['contexts'] = [self.object_to_model(context) for context in object.contexts]

            Model = self.get_model(self.get_object_name(object))

            return Model(**serialization)
        
        elif isinstance(object, Triple) and (object.subject or object.predicate or object.object):
            # Deal with nested entities and relationship
            if object.subject: serialization['subject'] = self.object_to_model(object.subject)
            if object.predicate: serialization['predicate'] = self.object_to_model(object.predicate)
            if object.object: serialization['object'] = self.object_to_model(object.object)

            Model = self.get_model(self.get_object_name(object))

            return Model(**serialization)

        else:
            # Non-nested structure
            Model = self.get_model(self.get_object_name(object))

            return Model(**serialization)

    def _query(self, element, **kwargs):
        """
        Return the coressponding element(s) by given condition.

        Protected method since the session cannot be exposed to the user.
        """
        from ..elements import Entity, Relationship, Statement, Triple

        session = kwargs.get('session', self.Session())

        serialization = element.serialize()
        
        import sqlalchemy
        empty_query = session.query(sqlalchemy.false()).filter(sqlalchemy.false())

        if isinstance(element, Relationship) and element.contexts:
            # Deal with nested statements
            # First, pick out the contexts parent
            # Then, query the relationship without statements
            # Finally, return the relationship if parent_id equals relationship_id

            # Filter the empty statements
            serialization['contexts'] = [
                self.object_to_model(context)
                for context in serialization['contexts']
                if context.id or context.text
            ]

            if not serialization['contexts']:
                # No nested statements left
                return self._query(element, session = session)

            # import pdb; pdb.set_trace()

            # Find the parent_id
            parents_id = []
            for statement in serialization['contexts']:
                result = self._query(statement, session = session).all()
                if not result:
                    # Cannot find the parent
                    return empty_query
                else:
                    parents_id.extend([item.relationship_id for item in result])

            if not parents_id:
                return empty_query

            parent_id = parents_id[0]
            for id in parents_id: 
                # Parent_ids are not identical
                if parent_id != id: return empty_query

            # Make a non-nested structure for next querying
            if serialization['contexts']: del serialization['contexts']
            return self._query(self.get_model('relationship')(**serialization), session = session).filter(self.get_model('relationship').id == parent_id)

        elif isinstance(element, Triple) and (element.subject or element.predicate or element.object):
            # Deal with nested entries
            # First, try to match the existed subject/ predicate/ object
            # Then, make a potential entry list for subject/ predicate/ object
            # Finally, find the non-nested structure which subject/ predicate/ object matchs respective list

            # Pop out subject, predicate, object
            if serialization['subject']:
                subjects_id = [item.id for item in self._query(serialization['subject'], session = session).all()]

            if serialization['predicate']:
                predicates_id = [item.id for item in self._query(serialization['predicate'], session = session).all()]

            if serialization['object']:
                objects_id = [item.id for item in self._query(serialization['object'], session = session).all()]

            # Construct the query condition by existances of the id lists
            condition = []
            # At least one of them has the value
            for item in ['subject', 'predicate', 'object']:
                try:
                    eval('%ss_id' % item)
                    condition.append("self.get_model('triple').{0}_id.in_({0}s_id)".format(item))
                except NameError:
                    pass
            condition = eval('&'.join(condition))

            # Make a non-nested structure for next querying
            if serialization['subject']: del serialization['subject']
            if serialization['predicate']: del serialization['predicate']
            if serialization['object']: del serialization['object']

            return self._query(self.get_model('triple')(**serialization), session = session).filter(condition)

        else:
            # Non-nested structure
            Model = self.get_model(self.get_object_name(element))

            filter_condition = dict([(key, value) for key, value in serialization.items() if value])

            return session.query(Model).filter_by(**filter_condition)


    def remove(self, element):
        """
        Removes the element(entity/relationship/statement/triple) that matches 
        the given element object and relatives. 
        Removes every fuzzy matched items if only given insufficient arguments.
        """
        session = self.Session()

        from ..elements import Entity, Relationship, Statement, Triple

        def remove_orphan_entities(session):
            EntityModel = self.get_model('entity')

            orphan_entity_record = session.query(EntityModel).filter(
                ~EntityModel.related_triples_as_sub.any() & ~EntityModel.related_triples_as_obj.any()
            ).all()

            for item in orphan_entity_record:
                session.delete(item)

        def remove_orphan_relationships(session):
            RelationshipModel = self.get_model('relationship')

            related_relationship_record = session.query(RelationshipModel).filter(
                ~RelationshipModel.related_triples_as_rel.any()
            ).all()

            for item in related_relationship_record:
                session.delete(item)
        
        if isinstance(element, Statement):
            # Delete statement(s) only
            statement_query = self._query(element, session = session).all()
            for item in statement_query:
                session.delete(item)

        elif isinstance(element, Relationship):
            # Delete relationship(s) and coressponding triples,then clear the orphan entities

            relationship_record = self._query(element, session = session).all()
            for item in relationship_record:
                session.delete(item)

            # Delete the orphan entities
            remove_orphan_entities(session)
            
        elif isinstance(element, Entity):
            # Delete entity or entities, and relative triples,then clear the orphans

            entity_record = self._query(element, session = session).all()
            for item in entity_record:
                session.delete(item)

            # Delete the orphan relationships
            remove_orphan_relationships(session)

            # Delete the orphan entities
            remove_orphan_entities(session)

        elif isinstance(element, Triple):
            # Delete the triple(s),then clear the orphans
            
            triple_record = self._query(element, session = session).all()
            for item in triple_record:
                session.delete(item)

            # Delete the orphan relationships
            remove_orphan_relationships(session)

            # Delete the orphan entities
            remove_orphan_entities(session)

        self._session_finish(session)

    def get_candidate_triples(self, entity):
        """
        Return a list of triples like <entity.type, ?, ?> and <?, ?, entity.type>,
        If entity.type is not existed,then return <entity.name, ?, ?> and <?, ?, entity.name>.
        """
        session = self.Session()

        TripleModel = self.get_model('triple')
        EntityModel = self.get_model('entity')

        if entity.type:
            # <entity.type, ?, ?> and <?, ?, entity.type>
            query = session.query(TripleModel).filter(
                entity.type == EntityModel.type
            ).filter(
                TripleModel.subject_id == EntityModel.id | 
                TripleModel.object_id == EntityModel.id
            )

        else:
            # <entity.name, ?, ?> and <?, ?, entity.name>
            query = session.query(TripleModel).filter(
                entity.name == EntityModel.name
            ).filter(
                TripleModel.subject_id == EntityModel.id | 
                TripleModel.object_id == EntityModel.id
            )
        
        all_relative_triples = query.all()

        for triple in all_relative_triples:
            yield self.model_to_object(triple)

        session.close()

    def create(self, triple):
        """
        Create a triple given an Triple object.
        Return the created triple.
        """
        session = self.Session()

        
        from sqlalchemy.exc import IntegrityError
        
        try:
            # Every entry is unique
            session.add(self.object_to_model(triple))

            self._session_finish(session)

        except IntegrityError:

            # Unique Constaint conflicts
            serialization = triple.serialize()

            # Check if exists identical subject
            candidate_subjects = self._query(serialization['subject'], session = session).all()
            if len(candidate_subjects) == 1: 
                serialization['subject_id'] = candidate_subjects[0].id
                serialization['subject'] = None

            # Check if exists identical predicate or just a contexts update
            contexts = serialization['predicate'].contexts
            candidate_predicates = self._query(serialization['predicate'], session = session).all()
            serialization['predicate'].contexts = None
            nc_candidate_predicates = self._query(serialization['predicate'], session = session).all()
            # 'nc' means 'no-contexts'
            if len(candidate_predicates) == 1:
                serialization['predicate_id'] = candidate_predicates[0].id
                serialization['predicate'] = None
            
            if not candidate_predicates and nc_candidate_predicates:
                # No result for contexts-contained predicate but has result for non-contexts predicate
                # Therefore, just a contexts update
                is_contexts_changed = False
                for context in contexts:
                    result = self._query(context, session = session).first()
                    if not result:
                        nc_candidate_predicates[0].contexts.append(self.object_to_model(context))
                        is_contexts_changed = True
                if is_contexts_changed:
                    session.add(nc_candidate_predicates[0])
                    serialization['predicate_id'] = nc_candidate_predicates[0].id
                    serialization['predicate'] = None

            # Check if exists identical object
            candidate_objects = self._query(serialization['object'], session = session).all()
            if len(candidate_objects) == 1: 
                serialization['object_id'] = candidate_objects[0].id
                serialization['object'] = None

            for item in ['subject', 'predicate', 'object']:
                if serialization[item]: 
                    serialization[item] = self.object_to_model(serialization[item])

            filter_condition = dict([(key, value) for key, value in serialization.items() if value])


            TripleModel = self.get_model('triple')
            triple = TripleModel(**filter_condition)

            candidate_triple = self._query(self.model_to_object(triple)).all()
            if not candidate_triple:
                session.add(triple)

            self._session_finish(session)

    def select(self, element):
        """
        Returns a list of objects that matches the given element object.
        """
        session = self.Session()

        query = self._query(element, session = session).all()

        for item in query:
            yield self.model_to_object(item)

        self._session_finish(session)

    def update(self, element):
        """
        Modifies an entry in the database.
        Creates an entry if one does not exist.
        """
        from ..elements import Entity, Relationship, Statement, Triple

        session = self.Session()
        record = None

        if element.id:
            record = session.query(self.get_model(self.get_object_name(element))).get(element.id)
        else:
            record = self._query(element, session = session).first()

        if not record:
            # No record found, Create a new one
            session.add(self.object_to_model(element))
        
        else:

            def fill_non_nested_attrs(fill_to, attr_dict, excluding = ['id']):
                for attr, value in attr_dict.items():
                    if value and attr not in excluding:
                        setattr(fill_to, attr, value)
            
            serialization = self.object_to_model(element).serialize()

            if isinstance(element, Relationship) and element.contexts:
                
                # Update non-nested part
                fill_non_nested_attrs(record, serialization, ['id', 'contexts'])

                # Update nested part
                for statement in serialization['contexts']:
                    result = self._query(statement, session = session).all()
                    if not result:
                        record.contexts.append(statement)

            elif isinstance(element, Triple) and element.predicate.contexts:

                # Update non-nested part
                fill_non_nested_attrs(record, serialization, ['id', 'predicate'])

                # Update nested part
                for statement in model.predicate.contexts:
                    result = self._query(statement, session = session).all()
                    if not result:
                        record.predicate.contexts.append(statement)

            else:
                fill_non_nested_attrs(record, model.serialize())
        
        session.add(record)

        self._session_finish(session)

    def drop(self):
        """
        Drop the database attached to a given adapter.
        """
        EntityModel = self.get_model('statement')
        RelationshipModel = self.get_model('relationship')
        StatementModel = self.get_model('statement')
        TripleModel = self.get_model('triple')

        session = self.Session()

        session.query(EntityModel).delete()
        session.query(RelationshipModel).delete()
        session.query(StatementModel).delete()
        session.query(TripleModel).delete()

        session.commit()
        session.close()

    def create_database(self):
        """
        Populate the database with the tables.
        """
        from ..ext.sqlalchemy_app.models import Base
        Base.metadata.create_all(self.engine)

    def _session_finish(self, session, element=None):
        from sqlalchemy.exc import InvalidRequestError
        try:
            session.commit()
        except InvalidRequestError:
            # Log the element and the exception
            self.logger.exception(element)
        finally:
            session.close()
