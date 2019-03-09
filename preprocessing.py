from bs4 import BeautifulSoup
import json_lines
from case import Case

def preprocess(file, max_lines=100, debug=True, train=False):
    cases = []
    count = 0

    if train:
        training_data_file = open('training-data.tsv','w')

    with open(file, 'rb') as f:
        reader = json_lines.reader(f)
        for i in range(max_lines):
            case = Case(next(reader))
            cases.append(case)

            if train:
                case.saveTrainingData(training_data_file)
            if debug:
                print(case.tuples)

    if train:
        training_data_file.close()

    return cases


# Update this to the correct jsonl file
cases = preprocess('/Users/kcurtis/Downloads/Arkansas-20180829-text/data/data.jsonl', max_lines=5)
