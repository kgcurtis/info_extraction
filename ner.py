from bs4 import BeautifulSoup
import spacy
from spacy import displacy

#output.txt is the file with text from the cases
infile = open('output.txt', 'r')

with open('output.txt') as file:
    [next(file) for x in range(100)]
    head = [next(file) for x in range(200)]

nlp = spacy.load('/path/to/saved/model')
doc = nlp(' '.join(head))
displacy.serve(doc, style='ent')
