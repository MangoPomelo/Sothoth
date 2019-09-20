class StatementMixin(object):
	"""
	This class has shared methods used to
	normalize different statement models.
	"""

	statement_field_names = [
		'id',
		'text',
		'relationship_id'
	]

	def get_statement_field_names(self):
		"""
		Return the list of entities for this statement.
		"""
		return self.statement_field_names

	def serialize(self):
		"""
		:returns: A dictionary representation of the statement object.
		:rtype: dict
		"""
		data = {}

		for field_name in self.get_statement_field_names():
			format_method = getattr(self, 'get_{}'.format(
				field_name
			), None)

			if format_method:
				data[field_name] = format_method()
			else:
				data[field_name] = getattr(self, field_name, None)

		return data



class Statement(StatementMixin):
	"""
	A statement represents a single spoken unit, sentence or
	phase, which is regard as a context indicating a specified
	relationship.
	"""

	__slots__ = (
		'id',
		'text',
		'storage',
	)

	def __init__(self, **kwargs):

		self.id = kwargs.get('id')
		self.text = kwargs.get('text')
		
		self.storage = None

	def __str__(self):
		return self.text

	def __repr__(self):
		return '<Statement(text:%s)>' % (self.text)

	def save(self):
		"""
		Save the statement in the database.
		"""
		self.storage.update(self)