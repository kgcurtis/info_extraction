# Repo Guide

## Named Entity Recognition

## WitAI implementation

#### Relevant files

- `extractor.py`: file containing the Spacy parser. It calls upon a `WitClient`
- `wit_client.py`: Takes text, breaks it into acceptable-length chunks (for WitAI API specs), then determines the relevant entities
Regarding
- `training_data/entities.csv`
- `training_data/training_data_ner.tsv`


## Relation Extraction

### Stanford coreNLP

Files to put into coreNLP folder:
- `coreNLP/server.properties`                         
- `coreNLP/ner-model.ser.gz`                          (custom trained NER model)
- `coreNLP/roth_relation_model_pipeline_2.ser`        (custom trained relationship extractor model)
- `stanford-corenlp.jar into coreNLP folder`  (recompiled corenlp classes to handle custom entities)

Other files:
- `coreNLP/RothCONLL04Reader.java`        (added support for custom entities)
- `coreNLP/RothEntityExtractor.java`      (added support for custom entities)
- `training_data/training_data_relations.corp`       (relationship extractor training data)
- `coreNLP/roth.properties`               (relationship extractor training properties file)

To start the server:
```
java -Xmx8g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000 -serverProperties server.properties
```

## neo4j

###### Relevant files:

- `neo4j/neo4j-fill.py`

To run this script, first follow the instructions below.

- Python 3.6+
- pip install neo4j
- a machine running the Neo4j server
- create a config.py file that looks like the following

```
username = 'your username'
password = 'your password'
instance = 'bolt://<IP address>:7867'
```

## Training Data Generation

##### Relevant files:

in `/training_data`:

  Data from IKE:
  - `Charges.dict.tsv`
  - `Convictions.dict.tsv`
  - `Sentences.dict.tsv`

  Generated training data files:
  - `training_data_ner.tsv` : used to train StanfordNER model
  - `training_data_relations.corp` : used to train coreNLP relationExtractor model

  Other:
  - `entities.csv`
