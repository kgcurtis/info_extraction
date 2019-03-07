from bs4 import BeautifulSoup
import json_lines
from case import Case

def preprocess(file, max_lines=100, debug=True):
    cases = []
    count = 0
    with open(file, 'rb') as f:
        for item in json_lines.reader(f):
            if count > max_lines:
                break
            case = Case(item)
            cases.append(case)
            if debug:
                print(case.get_tuples())

# Update this to the correct jsonl file
preprocess('/Users/kcurtis/Downloads/Arkansas-20180829-text/data/data.jsonl', max_lines=50)
