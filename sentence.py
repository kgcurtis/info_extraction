from word import Word

class Sentence:

    def __init__(self, sentence, entity1=None, entity2=None, relationship=None):
        self.sentence = sentence.split(" ")
        self.words = [None] * len(self.sentence)
        self.ind = 0
        self.entity1 = [entity1.lower(), -1] #we will find the correct indices later
        self.entity2 = [entity2.lower(), -1]
        self.relationship = relationship

    def add_word(self, word, pos):

        #Named entity here
        if self.words[self.ind] != None:
            self.words[self.ind].pos = pos
            self.ind+=1
            return

        self.words[self.ind] = Word(word, pos)
        self.ind+=1


    def add_named_entity(self, word, entity_type, begin, end):
        ne_list = word.split(" ")
        print(word, entity_type, begin, end)
        print(len(self.words))
        if begin != -1:
            ne_list_iter = iter(ne_list)
            for i in range(begin, end):
                self.words[i] = Word(next(ne_list_iter), entity_type=entity_type)

    #coreNLP is particular about entities with multiple tokens being all on one line
    #so we must combine them here
    def combine_named_entities(self):

        self.ind = 0
        combined = []

        while self.ind < len(self.words):
            word = self.words[self.ind]

            curr_words = []
            curr_words.append(word)

            while self.ind < (len(self.words) - 1) and self.words[self.ind + 1].is_same_entity(word):
                self.ind += 1
                word = self.words[self.ind]
                curr_words.append(word)


            full_word = ' '.join([w.word for w in curr_words])
            if self.entity1[1] == -1 and self.entity1[0] in full_word.lower():
                self.entity1[1] = self.ind - (len(curr_words) - 1)
            elif self.entity2[0] in full_word.lower():
                self.entity2[1] = self.ind - (len(curr_words) - 1)

            combined.append(curr_words[0]) if len(curr_words) == 1 else combined.append(curr_words)
            self.ind+=1

        self.words = combined



    #Format the sentence to align with what coreNLP is expecting
    def format_sentence(self, i):


        if self.valid_sentence():

        sentence = ""
        for ind, word in enumerate(self.words):
                if isinstance(word, list):
                    token = '/'.join(w.word for w in word)
                    pos = '/'.join(w.pos for w in word)
                    entity_type = word[0].entity_type
                else:
                    token = word.word
                    pos = word.pos
                    entity_type = word.entity_type
                if len(token) > 0:
                    sentence += "{0} {1} {2} O {3} {4} O O O\n".format(i, entity_type, ind, pos, token)

        if self.entity1 is not None:
            sentence += "\n{0} {1} {2}\n\n".format(self.entity1[1], self.entity2[1], self.relationship)

        return sentence

    def format_sentence_for_ner(self):

        sentence = ""
        for word in self.words:
            token = word.word
            entity_type = word.entity_type

            sentence += "{0}\t{1}\n".format(token, entity_type)

        sentence += "\n"
        return sentence

    def find_sub_list(self,sl,l):
        sll=len(sl)
        for ind in (i for i,e in enumerate(l) if e==sl[0]):
            if l[ind:ind+sll]==sl:
                return ind,ind+sll-1
        return (-1,-1)

    def valid_sentence(self):

        e1_type = ''
        e2_type = ''

        if self.entity1 is not None:
            if self.entity1[1] >= len(self.words) or self.entity2[1] >= len(self.words):
                return False
            if isinstance(self.words[self.entity1[1]], list):
                e1_type = self.words[self.entity1[1]][0].entity_type
            else:
                e1_type = self.words[self.entity1[1]].entity_type

            if isinstance(self.words[self.entity2[1]], list):
                e2_type = self.words[self.entity2[1]][0].entity_type
            else:
                e2_type = self.words[self.entity2[1]].entity_type

            if e1_type == 'O' or e2_type == 'O':
                return False
        return True
