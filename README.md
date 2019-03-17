## Coreference Resolution

To run this script, first install spaCy, beautiful soup, json_lines, and donwload the neuralcoref model.

```
pip install spacy==2.0.12
pip install beautifulsoup4
pip install json-lines
pip install https://github.com/huggingface/neuralcoref-models/releases/download/en_coref_sm-3.0.0/en_coref_sm-3.0.0.tar.gz
```

Next, go to: [Case Law](https://case.law/) and create an account. From there, navigate to [Bulk Download](https://case.law/bulk/download/) to download the caselaw data in bulk.
After downloading and extracting, navigate to the /data folder and extract that as well. Now, you will have a .jsonl file. If you run coref_resolution.py
from within this folder, it will resolve coreferences in the cases. This will take a very long time, so it may not be necessary to resolve the whole
.jsonl file at first.



## WitAI implementation
- `extractor.py`: file containing the Spacy parser. It calls upon a `WitClient`
- `wit_client.py`: Takes text, breaks it into acceptable-length chunks (for WitAI API specs), then determines the relevant entities
Regarding


## Stanford coreNLP

Files to put into coreNLP folder:
- server.properties                         
- ner-model.ser.gz                          (custom trained NER model)
- roth_relation_model_pipeline_2.ser        (custom trained relationship extractor model)
- stanford-corenlp.jar into coreNLP folder  (recompiled corenlp classes to handle custom entities)

Other files:
- RothCONLL04Reader.java        (added support for custom entities)
- RothEntityExtractor.java      (added support for custom entities)
- small/medium_train.corp       (relationship extractor training data)
- roth.properties               (relationship extractor training properties file)
 
### Then start the server:
```
java -Xmx8g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000 -serverProperties server.properties
```
