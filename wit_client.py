from wit import Wit
from textwrap import wrap
import pprint

pp = pprint.PrettyPrinter(indent = 4)

def getNestedKey(dictionary, path):
	if len(path) == 1:
		return dictionary.get(path[0]) or []

	newDict = dictionary.get(path[0])
	newPath = path[1:]
	return getNestedKey(newDict, newPath)


class WitClient:
	def __init__(self):
		self.client = Wit("WPNFYXIQFRSMV4SY7CQREJQFJIPRTPIV")

	def entities(self, msg):
		# Wit restrict msgs to len = 256; break msg up accordingly
		for phrase in wrap(msg, width = 256): 
			witResponse = self.client.message(phrase)

			caseNames = getNestedKey(witResponse, ["entities", "case_name"])
			for instance in caseNames:
				yield tuple(( "CASE_NAME", instance["value"] ))

			caseTypes = getNestedKey(witResponse, ["entities", "case_type"])
			for instance in caseTypes:
				yield tuple(( "CASE_TYPE", instance["value"] ))
				
			courtTypes = getNestedKey(witResponse, ["entities", "court_type"])
			for instance in courtTypes:
				yield tuple(( "COURT_TYPE", instance["value"] ))
				
			legalActions = getNestedKey(witResponse, ["entities", "legal_action"])
			for instance in legalActions:
				yield tuple(( "LEGAL_ACTION", instance["value"] ))
				
			legalDocuments = getNestedKey(witResponse, ["entities", "legal_documents"])
			for instance in legalDocuments:
				yield tuple(( "LEGAL_DOCUMENTS", instance["value"] ))
				
			legalPositions = getNestedKey(witResponse, ["entities", "legal_position"])
			for instance in legalPositions:
				yield tuple(( "LEGAL_POSITION", instance["value"] ))
				
			offenseTypes = getNestedKey(witResponse, ["entities", "offense_type"])
			for instance in offenseTypes:
				yield tuple(( "OFFENSE_TYPE", instance["value"] ))

