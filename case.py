from wit_client import WitClient
from spacy_client import Spacy
from openie_client import OpenIE
import string
from parser import CustomParser
import spacy
from spacy.matcher import Matcher

openie_client = OpenIE()
wit_client = WitClient()
spacy_client = Spacy()
spacy_client.add_states_pipe()
nlp = spacy.load("en_core_web_md")

numOfSentences = 25

key_terms = {
    "evidence": ("evidence", 2),
    "judgment": ("verdict", 2),
    "judgement": ("verdict", 2),
    "verdict": ("verdict", 2),
}
key_actions = {
    "admissible": "evidence",
    "issu": "verdict",
    "reject": "evidence"
}

crimes = set()
with open('crime_keywords.txt') as file:
    for crime in file.readlines():
        word = crime.rstrip()
        word = word.lower()
        crimes.add(word)


class Case:

    appeal_keywords = ['appeal', 'appellate']

    def __init__(self, info):
        self.case_name = info['name_abbreviation']
        self.court_name = info['court']['name']
        self.date = info['decision_date']

        self.text = ' '.join(opinion['text'] for opinion in info['casebody']['data']['opinions'])
        self.parser = CustomParser(self.text)
        self.appeal = ('appeal' in self.text or 'appeal' in self.court_name)

    def get_openie_relationships(self, text):
        relations = {}
        for relation in openie_client.extractOpenRelations(text):
            key = relation[0].lower()
            if key not in relations:
                relations[key] = relation

            cachedRelation = relations[key]
            if len(relation[-1]) > len(cachedRelation[-1]):
                relations[key] = relation

        print("   OpenIE API call resolved")
        for key, action, finale in relations.values():
            if key in key_terms:
                yield self.case_name, key_terms[key][0], relation[ key_terms[key][1] ]
            # Multi-word keys are probably less informative and/or duplicated
            elif " " in key:
                continue
            else:
                for key_action, action_type in key_actions.items():
                    if key_action in action or key_action in finale:
                        yield self.case_name, action_type, " ".join(relation[1:])

    def identify_crimes(self):
        seen = set()
        tokens = { phrase.text for phrase in self.parser.doc }
        for crime in crimes:
            for phrase in tokens:
                if crime in seen:
                    continue
                if crime in " " + phrase.lower():
                    seen.add(crime)
                    yield phrase

    def relationships(self, debug=True):
        print("Getting meta relationships")
        yield (self.case_name, 'decided on', self.date)

        if 'v.' in self.case_name:
            parties = self.case_name.split(' v. ')
            first = parties[0]
            second = parties[1]

            yield (first, 'against', second)
            if self.appeal:
                yield (self.case_name, 'appellant', first)
                yield (self.case_name, 'appellee', second)
            else:
                yield (self.case_name, 'plaintiff', first)
                yield (self.case_name, 'defendant', second)

        for state in self.states(self.court_name):
            yield (self.case_name, 'court location', state)
            if debug:
                print(state)

        print("Getting case references")
        for case in self.parser.case_names():
            if self.case_name != case:
                yield (self.case_name, 'references', case)

        print("Getting OpenIE relationships: ", end='')
        sentences = list(self.parser.doc.sents)
        print(len(sentences))
        def sentence_chunks():
            for i in range(0, len(sentences), numOfSentences):
                yield sentences[i: i + numOfSentences]
        for chunk in sentence_chunks():
            text = " ".join(sentence.text for sentence in chunk)
            for relation in self.get_openie_relationships(text):
                yield relation
                if debug:
                    print(relation)

        print("Getting crimes")
        for crime in self.identify_crimes():
            yield self.case_name, "prompted by", crime

    def states(self, msg):
        return (state for state in spacy_client.states(msg))
