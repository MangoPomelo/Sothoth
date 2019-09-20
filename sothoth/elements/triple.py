class TripleMixin(object):
	"""
	This class has shared methods used to
	normalize different triple models.
	"""

	triple_field_names = [
		'id',
		'subject_id',
		'predicate_id',
		'object_id',
		'subject',
		'predicate',
		'object',
	]

	def get_triple_field_names(self):
		"""
		Return the list of tags for this statement.
		"""
		return self.triple_field_names

	def serialize(self):
		"""
		:returns: A dictionary representation of the triple object.
		:rtype: dict
		"""
		data = {}

		for field_name in self.get_triple_field_names():
			format_method = getattr(self, 'get_{}'.format(
				field_name
			), None)

			if format_method:
				data[field_name] = format_method()
			else:
				data[field_name] = getattr(self, field_name, None)

		return data


class Triple(TripleMixin):
	"""
	A triple represents a coressponding triple
	reference in Knowledge Graph.
	"""

	__slots__ = (
		'id',
		'subject',
		'predicate',
		'object',
		'storage',
	)

	def __init__(self, **kwargs):

		self.id = kwargs.get('id')

		self.subject = kwargs.get('subject')
		self.predicate = kwargs.get('predicate')
		self.object = kwargs.get('object')

		self.storage = None

	def __str__(self):
		return '<%s, %s, %s>' % (self.subject, self.predicate, self.object)

	def __repr__(self):
		return '<Triple(subject:%s predicate:%s object:%s)>' % (self.subject, self.predicate, self.object)

	def save(self):
		"""
		Save the triple in the database
		"""
		self.storage.update(self)