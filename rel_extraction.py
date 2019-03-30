from bs4 import BeautifulSoup
import json_lines
from case import Case
import sys

def preprocess(file, case_index=0, num_cases=1, debug=True, train=False):
    cases = []
    count = 0

    upperBound = sys.maxsize
    if num_cases != "all":
        upperBound = case_index + num_cases
    else:
        num_cases = 100000

    with open(file, 'rb') as f:
        reader = json_lines.reader(f)

        idx = 0
        for rawCase in reader:
            # Quit once we exhaust our needs
            if idx >= upperBound:
                break

            # Skip cases that aren't in range
            if not case_index <= idx <= case_index + num_cases:
                idx += 1
                continue

            case = Case(rawCase)
            cases.append(case)
            relationships = set(case.relationships(debug = False))
                
            if debug:
                print("Case number: %s" % str(idx))
                # print(case.text)
                # for relationship in case.relationships(debug = False):
                #     print(relationship)
                # print(relationships)
                # print()

            with open("output.txt", "a") as file:
                for relation in relationships:
                    file.write(str(relation))
                    file.write("\n")

            idx += 1

    if train:
        training_data_file.close()

    return cases


# Update this to the correct jsonl file
cases = preprocess('data.jsonl', case_index = 0, num_cases = "all")