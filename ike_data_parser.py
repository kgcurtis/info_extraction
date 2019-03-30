import csv
import sys
from generator import Generator
import json
from sentence import Sentence
from wit_client import WitClient
from spacy_client import Spacy
from openie_client import OpenIE

wit_client = WitClient()
spacy_client = Spacy()
openie_client = OpenIE()

def get_entities(msg):

    openie_entities = { value : {"entity_type": entity_type, "begin" : begin, "end" : end } for entity_type, value, begin, end in openie_client.entities(msg) }

    return openie_entities

def find_sub_list(sl,l):
    sll=len(sl)
    for ind in (i for i,e in enumerate(l) if e==sl[0]):
        if l[ind:ind+sll]==sl:
            return ind,ind+sll-1
    return (-1,-1)

def crime_entity_data(sentence, crime):
    tokens = sentence.split(" ")
    crime_words = crime.split(" ")

    (begin, end) = find_sub_list(crime_words, tokens)
    return { "entity_type": 'CRIMINAL_CHARGE', "begin" : begin, "end" : end + 1 }

def parse_file(filename, relationship, sentence_ind, output_file, ner=False):

    with open(filename) as tsvfile:
        tsvreader = csv.reader(tsvfile, delimiter="\t")
        gen = Generator()

        # pass the header
        tsvfile.readline()

        for line in tsvreader:
            if(line[2] == 'positive'): # we are only training positive examples
                # retrieve entities that ike extracted
                party = line[0]
                crime = line[1]
                context = json.loads(line[3])['context'][0]
                fragment = context['fragment']
                words = context['words']

                # retrieve entities from openie
                entities = get_entities(fragment)
                entities[crime] = crime_entity_data(fragment, crime)

                # create the sentnece object with the specific relation
                s = Sentence(fragment, party, crime, relationship)

                # annotate the named entities
                for token in entities:
                    s.add_named_entity(token, entities[token]['entity_type'], entities[token]['begin'], entities[token]['end'])

                # annotate pos
                for word in words:
                    token = word['word']
                    pos = word['attributes']['pos']
                    s.add_word(token, pos)

                # combine named entities, because of coreNLP trainig data format specifications
                s.combine_named_entities()

                # write sentence in specific coreNLP format
                out = s.format_sentence(sentence_ind)
                output_file.write(out)

                # if the sentence was invalid, don't increment
                if out is not "":
                    sentence_ind += 1

        return sentence_ind

file_list = [('training_data/Charges.dict.tsv', 'charged_with'), ('training_data/Convictions_v1.dict.tsv','convicted_of'), ('training_data/Sentences.dict.tsv','sentenced_with')]
output_file = open('training_data/training_data_relations.corp','w')

# because we are ingesting multiple files, we need to keep a global sentence counter
sentence_ind = 0
for f in file_list:
    sentence_ind = parse_file_no_rel(f, sentence_ind, output_file)

o_file.close()
