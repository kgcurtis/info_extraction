from itertools import chain
import spacy
from spacy.matcher import Matcher
nlp = spacy.load("en_core_web_md")

class CustomParser:
	def __init__(self, text, synonyms = []):
		self.text = text
		self.doc = nlp(self.text)
		self.condense_noun_chunks()

		self.cases = set()

	'''
		Condense additional undetected noun chunks
	'''
	def condense_noun_chunks(self):
		# Merge explicitly-identified noun chunks
		ranges = [ (chunk.start, chunk.end) for chunk in self.doc.noun_chunks ]
		with self.doc.retokenize() as retokenizer:
			for (start, end) in self.condense_token_ranges(ranges):
				retokenizer.merge(self.doc[start:end], attrs={"POS": "NOUN"})

		# Merge implicitly-known noun chunks
		chunk_matcher = Matcher(nlp.vocab)
		pattern__noun_noun = [
			{"POS": "NOUN", "OP": "+"},
			{"POS": "ADP", "OP": "?"},
			{"POS": "NOUN", "OP": "+"}
		] # e.g., "theft of property"
		chunk_matcher.add("noun_prep_noun", None, pattern__noun_noun)
		pattern__action_noun = [
			{"TAG": "VBG"},
			{"POS": "NOUN"}
		] # e.g., "transporting drugs"
		chunk_matcher.add("action_noun", None, pattern__action_noun)

		ranges = [ (start, end) for (ID, start, end) in chunk_matcher(self.doc) ]
		with self.doc.retokenize() as retokenizer:
			for (start, end) in self.condense_token_ranges(ranges):
				retokenizer.merge(self.doc[start:end], attrs={"POS": "NOUN"})

	@staticmethod
	def condense_token_ranges(ranges):
		flatten = chain.from_iterable
		LEFT, RIGHT = 1, -1
		offset = 0

		data = sorted(flatten(((start, LEFT), (stop + offset, RIGHT)) for start, stop in ranges))
		c = 0
		for value, label in data:
			if c == 0:
			    x = value
			c += label
			if c == 0:
			    yield x, value - offset

	def case_names(self):
		doc = nlp(self.text)

		case_matcher = Matcher(nlp.vocab)
		pattern = [
			{"POS": "PROPN", "OP": "+"},
			{"ORTH": "v."},
			{"POS": "PROPN", "OP": "+"}
		]
		case_matcher.add("case", None, pattern)

		ranges = [ (start, end) for (ID, start, end) in case_matcher(doc) ]
		for (start, end) in self.condense_token_ranges(ranges):
			yield ' '.join(token.text for token in doc[start:end])
