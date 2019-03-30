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
            for rel in rels:
                yield rel['subject'], rel['relation'], rel['object']

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

    def entities(self, msg):

        url = 'http://localhost:9000/'
        params = {'properties':'{"annotators":"ner","outputFormat":"json"}'}

        r = requests.post(url, params=params, data=msg.encode('utf-8'))

        sentences = r.json()['sentences']
        for sentence in sentences:
            entities = sentence['entitymentions']
            for entity in entities:
                yield(entity['ner'], entity['text'], entity['docTokenBegin'], entity['docTokenEnd'])
