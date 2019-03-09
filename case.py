from wit_client import WitClient
from spacy_client import Spacy
from openie_client import OpenIE
import string
from textwrap import wrap
import re

openie_client = OpenIE()
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

        for relation in openie_client.extractRelationships(self.text):
            self.tuples.append(relation)
            if debug:
                print(openie_rels)


    def saveTrainingData(self, output_file):
        for sentence in self.generateTrainingData(self.text):
            for item in sentence:
                output_file.write(item + "\n")
            output_file.write('\n')

    def generateTrainingData(self, msg):

        translator = str.maketrans('', '', string.punctuation)
        msg = self.text.translate(translator)

        wordDict = {}

        #Get legal entity annotations from wit
        for entity, value in wit_client.entities(msg):
            valueArr = value.split(' ')
            for item in valueArr:
                wordDict[item] = entity

        #Get all other entity annotations from spacy
        for entity, value in spacy_client.people(msg):
            valueArr = value.split(' ')
            for item in valueArr:
                wordDict[item] = entity

        #Create the tab separated training data
        sentence = []
        for word in re.findall(r"[\w']+|[.,!?;]", self.text):
            if word in wordDict:
                sentence.append(word + "\t" + wordDict[word])
            else:
                sentence.append(word + "\tO")
        yield sentence


    def legal_entities(self, msg):
     return ((entity, value) for entity, value in wit_client.entities(msg))

    def states(self, msg):
        return (state for state in spacy_client.states(msg))
