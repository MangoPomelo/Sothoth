"""
constants
"""

'''
The maximum length of characters that the text of a statement can contain.
The number 255 is used because that is the maximum length of a char field
in most databases. This value should be enforced on a per-model basis by
the data model for each storage adapter.
'''
STATEMENT_TEXT_MAX_LENGTH = 255

# The maximum length of characters that the attribution of a(n) entity/relationship can contain.
ATTR_MAX_LENGTH = 50