import sys
from training_data_generator import TrainingDataGenerator

generator = TrainingDataGenerator()

input_name = sys.argv[1].rsplit(".", 1)[0]
output_file = open(input_name +'_training_data.tsv','w')

with open(sys.argv[1], 'r') as f:
    ind = 0
    items = []
    for item in f:
        items.append(item)

    for item in items:
        for sentence in generator.generateRelationshipTrainingData(item):
            for word in sentence:
                output_file.write(str(ind) + " " + word + "\n")
            ind+=1
            output_file.write("\n")

    for item in items:
        for sentence in generator.generateNamedEntityTrainingData(item):
            for item in sentence:
                output_file.write(item + "\n")
            output_file.write("\n")
