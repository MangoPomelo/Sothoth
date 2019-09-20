"""
Text pre-processors.
"""


def clean_whitespace(text):
    """
    Remove any consecutive whitespace characters from the text text.
    """
    import re

    # Replace linebreaks and tabs with spaces
    text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')

    # Remove any leeding or trailing whitespace
    text = text.strip()

    # Remove consecutive spaces
    text = re.sub(' +', ' ', text)

    return text


def unescape_html(text):
    """
    Convert escaped html characters into unescaped html characters.
    For example: "&lt;b&gt;" becomes "<b>".
    """
    import html

    text = html.unescape(text)

    return text


def convert_to_ascii(text):
    """
    Converts unicode characters to ASCII character equivalents.
    For example: "på fédéral" becomes "pa federal".
    """
    import unicodedata

    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('utf-8')

    return text

def convert_to_lower_case(text):
    """
    Converts upper characters to lower character equivalents.
    For example: "He is here" becomes "he is here".
    """
    text = text.lower()

    return text
