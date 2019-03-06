import csv
import spacy
import random
from spacy.matcher import Matcher
from spacy.gold import GoldParse
from spacy.language import EntityRecognizer
from spacy.util import minibatch, compounding
from pathlib import Path

entities = {'Court Type': 'COURT_TYPE', 'Case Type': 'CASE_TYPE', 'Legal Action': 'LEGAL_ACTION', 'Legal Position':'LEGAL_POS', 'Legal Document':'LEGAL_DOC','Offense Type':'OFFENSE_TYPE'}
entity_gold_standard = {}


with open('entities.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count < 9:
            # Ignore header in csv
            pass
        else:
            entity_gold_standard[row[1]] = entities[row[0]]
        line_count += 1


# Create dictionary of entity types and examples
gold_standard_buckets = {}
for entity_type in entities:
    gold_standard_buckets[entities[entity_type]] = []

for item in entity_gold_standard:
    gold_standard_buckets[entity_gold_standard[item]].append(item)

print(gold_standard_buckets)
print('\n\n\n\n\n')

# Find instances of these entities in the text using Matcher
nlp = spacy.load('en_core_web_sm')
matcher = Matcher(nlp.vocab)

# Add case insensitive matches to matcher object
for entity_type in gold_standard_buckets:
    for text in gold_standard_buckets[entity_type]:
        arr = [{'LOWER':text.lower()}]
        matcher.add(entity_type, None, arr)

# Read first 100 lines of textfile (too big otherwise)
with open('output.txt') as file:
    head = [next(file) for x in range(100)]

doc = nlp(' '.join(head))
# Find matches in doc
matches = matcher(doc)

TRAIN_DATA = []
for match_id, start, end in matches:


    match_type = nlp.vocab.strings[match_id] # Entity type
    match_text = doc[start:end].text         # Entity example
    sentence = doc[start - 15 : end + 15]    # Sentence spanning 15 words on either side, containing the example

    start_offset = len(doc[start - 15 : start].text + " ")
    end_offset = start_offset + len(match_text)

    print(match_type, start, end, match_text)
    print(sentence.text)
    print('NEW Annotation: ', start_offset, end_offset, len(sentence.text), match_text)
    print('\n\n')

    # Add example sentence to the training set
    train_data_item = (sentence.text, {"entities": [(start_offset, end_offset, match_type)]})
    TRAIN_DATA.append(train_data_item)


nlp = spacy.load('en_core_web_sm')
ner = nlp.get_pipe("ner")

# add labels
for _, annotations in TRAIN_DATA:
    for ent in annotations.get("entities"):
        ner.add_label(ent[2])

# get names of other pipes to disable them during training
other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
with nlp.disable_pipes(*other_pipes):  # only train NER
    # reset and initialize the weights randomly – but only if we're
    # training a new model

    nlp.begin_training()
    for itn in range(100):
        random.shuffle(TRAIN_DATA)
        losses = {}
        # batch up the examples using spaCy's minibatch
        batches = minibatch(TRAIN_DATA, size=compounding(4.0, 32.0, 1.001))
        for batch in batches:
            texts, annotations = zip(*batch)
            nlp.update(
                texts,  # batch of texts
                annotations,  # batch of annotations
                drop=0.5,  # dropout - make it harder to memorise data
                losses=losses,
            )
        print("Losses", losses)

# test the trained model
for text, _ in TRAIN_DATA:
    doc = nlp(text)
    print("Entities", [(ent.text, ent.label_) for ent in doc.ents])
    print("Tokens", [(t.text, t.ent_type_, t.ent_iob) for t in doc])

# save model to output directory
output_dir = '/path/to/saved/model/'
if output_dir is not None:
    output_dir = Path(output_dir)
    if not output_dir.exists():
        output_dir.mkdir()
    nlp.to_disk(output_dir)
    print("Saved model to", output_dir)

    # test the saved model
    print("Loading from", output_dir)
    nlp2 = spacy.load(output_dir)
    for text, _ in TRAIN_DATA:
        doc = nlp2(text)
        print("Entities", [(ent.text, ent.label_) for ent in doc.ents])
        print("Tokens", [(t.text, t.ent_type_, t.ent_iob) for t in doc])
