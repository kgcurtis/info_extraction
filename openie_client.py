import requests

class OpenIE:
    def extractRelationships(self, msg):

        url = 'http://localhost:9000/'
        params = {'properties':'{"annotators":"ner,openie","outputFormat":"json"}'}
        
        r = requests.post(url, params=params, data=msg.encode('utf-8'))
        sentences = r.json()['sentences']

        relationships = []
        for sentence in sentences:
            rels = sentence['openie']
            relationships.extend([(rel['subject'], rel['relation'], rel['object']) for rel in rels])
        return relationships
