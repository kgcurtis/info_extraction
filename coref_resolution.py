from bs4 import BeautifulSoup
import spacy
from spacy import displacy
import json_lines

nlp = spacy.load('en_coref_sm')
text_file = open('output.txt','w')
with open('data.jsonl', 'rb') as f:
    for item in json_lines.reader(f):
        name = item['name']
        date = item['decision_date']
        court_name = item['court']['name']
        text = ''
        for opinion in item['casebody']['data']['opinions']:
            text += opinion['text']

        text_to_annotate = name + " was a court case decided on " + date + " in " + court_name + ". " + name + " is this. " + text
        doc = nlp(text_to_annotate)
        resolved = doc._.coref_resolved
        print('Resolved...' + resolved + '\n\n')
        text_file.write(resolved)
        text_file.write('\n\n')


text_file.close()
