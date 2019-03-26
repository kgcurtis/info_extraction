import requests
import pprint

class OpenIE:
    def extractOpenRelations(self, msg):

        url = 'http://localhost:9000/'
        params = {'properties':'{"annotators":"ner,openie","outputFormat":"json"}'}

        r = requests.post(url, params=params, data=msg.encode('utf-8'))
        sentences = r.json()['sentences']

        relationships = []
        for sentence in sentences:
            rels = sentence['openie']
            relationships.extend([(rel['subject'], rel['relation'], rel['object']) for rel in rels])

        return relationships

    def extractTargetedRelations(self, msg):

        url = 'http://localhost:9000/'
        params = {'properties':'{"annotators":"ner,relation","outputFormat":"text"}'}

        r = requests.post(url, params=params, data=msg.encode('utf-8'))
        print(r.text)


    def annotateSentences(self, msg):

        url = 'http://localhost:9000/'
        params = {'properties':'{"annotators":"pos","outputFormat":"json"}'}

        r = requests.post(url, params=params, data=msg.encode('utf-8'))

        sentences = r.json()['sentences']

        for sentence in sentences:
            tokens = sentence['tokens']
            yield [(word['word'], word['pos']) for word in tokens]
