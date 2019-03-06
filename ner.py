from bs4 import BeautifulSoup
import spacy
from spacy import displacy

#output_small.txt is the file with text from the cases
infile = open('output_small.txt', 'r')

nlp = spacy.load('/path/to/saved/model')
doc = nlp(infile.read())
displacy.serve(doc, style='ent')
