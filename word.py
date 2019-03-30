
class Word:

    def __init__(self, word, pos=None, entity_type='O'):
        self.word = word
        self.pos = pos
        self.entity_type = entity_type

    def __str__(self):
        return self.word + " (" + self.entity_type + ")"

    def __repr__(self):
        return self.__str__()

    def is_same_entity(self, word):
        return self.entity_type == word.entity_type and self.entity_type != 'O'
