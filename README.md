# Sothoth
A generic QA answer bot framework based on triples  
The structure is based on [Chatterbot](https://github.com/gunthercox/ChatterBot)  

## Language independent
- Use NLTK tokenizer, tagger, named entity recognizer defaultly, you can use other corresponding tools on your language.
- To do that, inherit the class from tokenizers.py, taggers.py, recognizers.py.

## Database independent
- Use sqlalchemy to construct ORM, which can be configured to link Mysql or other types of databases.

## Algorithm independent
- Entity similarity and context similarity algorithms are in the ./sothoth/comparisons/, inherit your own if you want
