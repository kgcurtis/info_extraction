import spacy
import random
from spacy.matcher import Matcher
from spacy.gold import GoldParse
from spacy.language import EntityRecognizer
from spacy.language import Language
from spacy.util import minibatch, compounding
from pathlib import Path
from states_pipeline import States

class Spacy:
    def __init__(self, model='en_core_web_sm'):
        self.nlp = spacy.load(model)
        self.ner = self.nlp.get_pipe("ner")

    def add_states_pipe(self):
        component = States(self.nlp)
        self.nlp.add_pipe(component, before='tagger')

    def train(self, training_data, iter=100):
        for _, annotations in training_data:
            for ent in annotations.get("entities"):
                self.ner.add_label(ent[2])

        # get names of other pipes to disable them during training
        other_pipes = [pipe for pipe in self.nlp.pipe_names if pipe != "ner"]
        with self.nlp.disable_pipes(*other_pipes):  # only train NER
            # reset and initialize the weights randomly – but only if we're
            # training a new model

            self.nlp.begin_training()
            for itn in range(iter):
                random.shuffle(training_data)
                losses = {}
                # batch up the examples using spaCy's minibatch
                batches = minibatch(training_data, size=compounding(4.0, 32.0, 1.001))
                for batch in batches:
                    texts, annotations = zip(*batch)
                    self.nlp.update(
                        texts,  # batch of texts
                        annotations,  # batch of annotations
                        drop=0.5,  # dropout - make it harder to memorise data
                        losses=losses,
                    )
                print("Losses", losses)

    def save_model(self, output_dir):
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()
        self.nlp.to_disk(output_dir)
        print("Saved model to", output_dir)


    def test(self, test_data):
        for text, _ in test_data:
            doc = self.nlp(text)
            print("Entities", [(ent.text, ent.label_) for ent in doc.ents])
            print("Tokens", [(t.text, t.ent_type_, t.ent_iob) for t in doc])
            print("States", [token.text for token in doc if token._.is_state])

    def entities(self, msg):
        doc = self.nlp(msg)
        return ((ent.text, ent.label_) for ent in doc.ents)

    def people(self, msg):
        doc = self.nlp(msg)
        return ((ent.label_, ent.text) for ent in doc.ents if ent.label_ is 'PERSON')

    def sentences(self, msg):
        doc = self.nlp(msg)
        return doc.sents

    def states(self, msg):
        doc = self.nlp(msg)
        return (token.text for token in doc if token._.is_state)
