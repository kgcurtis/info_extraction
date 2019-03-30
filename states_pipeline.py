from spacy.tokens import Token, Span
from spacy.matcher import PhraseMatcher
import json
import requests

class States(object):
    name = 'states'  # component name shown in pipeline

    def __init__(self, nlp, label='GPE'):
        # load list of states from json file
        json_data = open('50_states.json').read()
        self.states = json.loads(json_data)

        self.matcher = PhraseMatcher(nlp.vocab)
        self.matcher.add('STATES', None, *[nlp(c) for c in self.states.values()])
        self.label = nlp.vocab.strings[label] # get label ID from vocab
        # register extensions on the Token
        Token.set_extension('is_state', default=False)

    def __call__(self, doc):
        matches = self.matcher(doc)
        spans = []  # keep the spans for later so we can merge them afterwards
        for _, start, end in matches:
            # create Span for matched country and assign label
            entity = Span(doc, start, end, label=self.label)
            spans.append(entity)
            for token in entity:  # set values of token attributes
                token._.set('is_state', True)
        doc.ents = list(doc.ents) + spans  # overwrite doc.ents and add entities – don't replace!
        for span in spans:
            span.merge()  # merge all spans at the end to avoid mismatched indices
        return doc  # don't forget to return the Doc!
