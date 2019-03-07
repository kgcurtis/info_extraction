from wit_client import WitClient
from spacy_client import Spacy

wit_client = WitClient()
spacy_client = Spacy()
spacy_client.add_states_pipe()

class Case:

    appeal_keywords = ['appeal', 'appellate']


    def __init__(self, info):

        self.case_name = info['name_abbreviation']
        self.court_name = info['court']['name']
        self.text = ' '.join([opinion['text'] for opinion in info['casebody']['data']['opinions']])
        self.appeal = ('appeal' in self.text or 'appeal' in self.court_name)

        self.tuples = []
        self.generate_tuples()


    def generate_tuples(self, debug=False):

        self.tuples.append((self.case_name, 'was tried in', self.court_name))

        if 'v.' in self.case_name:
            parties = self.case_name.split(' v. ')
            first = parties[0]
            second = parties[1]

            self.tuples.append((first, ' against ', second))
            if self.appeal:
                self.tuples.append((first, ' held the role of ', 'appellant'))
                self.tuples.append((second, ' held the role of ', 'appellee'))
            else:
                self.tuples.append((first, ' held the role of ', 'plaintiff'))
                self.tuples.append((second, ' held the role of ', 'defendant'))

        for entity, value in self.legal_entities(self.court_name):
            self.tuples.append((self.case_name, ' court type was ', value))
            if debug:
                print("%s: %s" % (entity, value))

        for state in self.states(self.court_name):
            self.tuples.append((self.case_name, ' court location was ', state))
            if debug:
                print(state)

        # use relationship extraction on the case text here?
        # print('legal entities in TEXT ******')
        # for entity, value in self.legal_entities(self.text):
        #     print("%s: %s" % (entity, value))


    def legal_entities(self, msg):
     return ((entity, value) for entity, value in wit_client.entities(msg))

    def states(self, msg):
        return (state for state in spacy_client.states(msg))

    def get_tuples(self):
        return self.tuples

    def text(self):
        return self.text
