class RelationshipMixin(object):
	"""
	This class has shared methods used to
	normalize different relationship models.
	"""

	relationship_field_names = [
		'id',
		'type',
		'contexts',
		'subject_type',
		'object_type',
	]

	def get_relationship_field_names(self):
		"""
		Return the list of tags for this statement.
		"""
		return self.relationship_field_names

	def get_contexts(self):
		"""
		Return the list of linking contexts for this relationship.
		"""
		return self.contexts

	def add_contexts(self, *statements):
		"""
		Add a list of linking contexts to the relationship.
		"""
		self.contexts.extend(statements)

	def serialize(self):
		"""
		:returns: A dictionary representation of the relationship object.
		:rtype: dict
		"""
		data = {}

		for field_name in self.get_relationship_field_names():
			format_method = getattr(self, 'get_{}'.format(
				field_name
			), None)

			if format_method:
				data[field_name] = format_method()
			else:
				data[field_name] = getattr(self, field_name, None)

		return data


class Relationship(RelationshipMixin):
	"""
	A relationship represents a coressponding relationship
	reference in Knowledge Graph.
	"""

	__slots__ = (
		'id',
		'type',
		'contexts',
		'subject_type',
		'object_type',
		'storage',
	)

	def __init__(self, **kwargs):

		self.id = kwargs.get('id')
		self.type = kwargs.get('type')
		self.contexts = kwargs.get('contexts', [])
		
		self.subject_type = kwargs.get('subject_type')
		self.object_type = kwargs.get('object_type')

		self.storage = None

	def __str__(self):
		return self.type

	def __repr__(self):
		return '<Relationship(type:%s subject_type:%s object_type:%s)>' % (self.type, self.subject_type, self.object_type)

	def save(self):
		"""
		Save the relationship in the database
		"""
		self.storage.update(self)