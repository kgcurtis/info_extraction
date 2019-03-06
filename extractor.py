import spacy
from wit_client import WitClient

client = WitClient()

class Parser:
	def __init__(self):
		self.nlp = spacy.load("en_core_web_sm")

	def entities(self, msg, debug = True):
		doc = self.nlp(msg)

		if debug:
			print(msg)
			print()

		# Get all Spacy entities
		for entity in doc.ents:
			if entity.text.strip():
				yield (entity.label_, entity.text.strip())

		# Get all legal entities
		for entity, value in client.entities(msg):
			yield (entity, value)

parser = Parser()
with open("output_small.txt") as file:
	text = ' '.join(file.readlines())

	for entity, value in parser.entities(text):
		print("%s: %s" % (entity, value))
