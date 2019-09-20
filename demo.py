from sothoth import Answeroid

def demo():

        from sothoth.elements import Triple, Entity, Relationship, Statement

        triples = [
                Triple(subject=Entity(name='Obama', type='PERSON'),
                       predicate=Relationship(type='IDENTITY', subject_type='PERSON', object_type='OCCUPATION',
                                              contexts=[
                                                            Statement(text='What is <PERSON>`s job'), 
                                                            Statement(text='What does <PERSON> do'),
                                                            Statement(text='Who is <PERSON>')
                                              ]
                       ),
                       object=Entity(name='American president', type='OCCUPATION')
                ),
                Triple(subject=Entity(name='Obama', type='PERSON'),
                       predicate=Relationship(type='BIRTHDAY', subject_type='PERSON', object_type='DATE',
                                              contexts=[
                                                            Statement(text='When was <PERSON> born'), 
                                                            Statement(text='What is <PERSON>`s birthday'),
                                                            Statement(text='What is date of <PERSON>`s birth')
                                              ]
                       ),
                       object=Entity(name='Aug 04, 1961', type='DATE')
                ),
                Triple(subject=Entity(name='Obama', type='PERSON'),
                       predicate=Relationship(type='BIRTHPLACE', subject_type='PERSON', object_type='PLACE',
                                              contexts=[
                                                            Statement(text='Where was <PERSON> born'),
                                                            Statement(text='What is the birthplace of <PERSON>')
                                              ]
                       ),
                       object=Entity(name='Honolulu, HI', type='PLACE')
                ),
                Triple(subject=Entity(name='Obama', type='PERSON'),
                       predicate=Relationship(type='AGE', subject_type='PERSON', object_type='NUMBER',
                                              contexts=[
                                                            Statement(text='How old is <PERSON>'),
                                                            Statement(text='What`s the age of <PERSON>'),
                                                            Statement(text='What`s <PERSON>`s age')
                                              ]
                       ),
                       object=Entity(name='58', type='NUMBER')
                )
        ]

        print('Initializing ...')

        answeroid = Answeroid(sent_comparator = 'sothoth.comparisons.sent_comparators.CosineSimilarity')

        answeroid.learn_knowledge(triples)

        try:
            while True:
                question = input('>>> ')
                if not question: continue
                response = answeroid.get_answer(question)
                for each_answer in response:
                    print(each_answer)
        except (KeyboardInterrupt, EOFError):
                print('\nBye')

if __name__ == '__main__':
        demo()