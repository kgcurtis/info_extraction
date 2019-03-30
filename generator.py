from wit_client import WitClient
from spacy_client import Spacy
from openie_client import OpenIE
import re

class Generator:

    def __init__(self):
        self.openie_client = OpenIE()
        self.wit_client = WitClient()
        self.spacy_client = Spacy()

    def generateNamedEntityTrainingData(self, msg):

        wordDict = {}

        #Get legal entity annotations from wit
        for entity, value in self.wit_client.entities(msg):
            valueArr = value.split(' ')
            for item in valueArr:
                wordDict[item] = entity

        #Get all other entity annotations from spacy
        for entity, value in self.spacy_client.people(msg):
            valueArr = value.split(' ')
            for item in valueArr:
                wordDict[item] = entity

        #Create the tab separated training data
        sentence = []
        for word in re.findall(r"[\w']+|[.,!?;]", msg):
            if word in wordDict:
                sentence.append(word + "\t" + wordDict[word])
            else:
                sentence.append(word + "\tO")
        yield sentence

    def generateRelationshipTrainingData(self, msg):

        wordDict = {}

        for entity, value, _, _ in self.openie_client.entities(msg):
            valueArr = value.split(' ')
            for item in valueArr:
                wordDict[item] = entity

        #Get legal entity annotations from wit
        for entity, value in self.wit_client.entities(msg):
            valueArr = value.split(' ')
            for item in valueArr:
                wordDict[item] = entity

        #Get all other entity annotations from spacy
        for entity, value in self.spacy_client.people(msg):
            valueArr = value.split(' ')
            for item in valueArr:
                wordDict[item] = entity

        annotated_sentences = self.openie_client.annotateSentences(msg)

        sentences = []
        for sentence in annotated_sentences:
            ind = 0
            sentence_data = []
            for word, pos in sentence:
                word_training_data = " " + str(ind) + " O " + pos + " " + word + " O O O"
                if word in wordDict:
                    word_training_data = wordDict[word] + word_training_data
                else:
                    word_training_data = "O" + word_training_data
                sentence_data.append(word_training_data)
                ind+=1
            sentences.append(sentence_data)
        return sentences
