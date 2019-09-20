class EntityMixin(object):
    """
    This class has shared methods used to
    normalize different entity models.
    """

    entity_field_names = [
        'id',
        'name',
        'type',
    ]

    def get_entity_field_names(self):
        """
        Return the list of tags for this statement.
        """
        return self.entity_field_names

    def serialize(self):
        """
        :returns: A dictionary representation of the entity object.
        :rtype: dict
        """
        data = {}

        for field_name in self.get_entity_field_names():
            format_method = getattr(self, 'get_{}'.format(
                field_name
            ), None)

            if format_method:
                data[field_name] = format_method()
            else:
                data[field_name] = getattr(self, field_name, None)

        return data

class Entity(EntityMixin):
    """
    An entity represents a coressponding entity
    reference in Knowledge Graph.
    """

    __slots__ = (
        'id',
        'name',
        'type',
        'storage',
    )

    def __init__(self, **kwargs):

        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.type = kwargs.get('type')

        self.storage = None

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Entity(name:%s type:%s)>' % (self.name, self.type)

    def save(self):
        """
        Save the entity in the database
        """
        self.storage.update(self)