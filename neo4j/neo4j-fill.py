from neo4j import GraphDatabase, basic_auth
import config
import sys
class CaseLawNeoDB(object):
    def __init__(self, uri, user, pw):
        creds = basic_auth(user, pw)
        self.driver = GraphDatabase.driver(uri, auth=creds)

    def close(self):
        self.driver.close()

# base functions
def merge_party_rel_party(tx, sro, rel):
    cmd = (
            'MERGE (p:Party {name:$nameA}) '
            'MERGE (q:Party {name:$nameB}) '
            'MERGE (p)-[r:%s]->(q)' % rel
            )
    tx.run(cmd, nameA=sro[0], nameB=sro[2])

## careful here, subject and object are purposely flipped,
## hence the indicies are inversed (sro[2] and sro[0])
def merge_party_rel_case(tx, sro, rel):
    cmd = (
            'MERGE (p:Party {name:$nameA}) '
            'MERGE (c:Case {name:$nameB}) '
            'MERGE (p)-[r:%s]->(c)' % rel
            )
    tx.run(cmd, nameA=sro[2], nameB=sro[0])

def merge_case_rel_attr(tx, sro, rel, attr):
    cmd = (
            'MERGE (c:Case {name:$nameA}) '
            'MERGE (a:%s {name:$nameB}) '
            'MERGE (c)-[r:%s]->(a)'
            ) % (attr, rel)
    tx.run(cmd, nameA=sro[0], nameB=sro[2])

def merge_party_rel(tx, sro, rel, attr):
    cmd = (
            'MERGE (c:Party {name:$nameA}) '
            'MERGE (a:%s {name:$nameB}) '
            'MERGE (c)-[r:%s]->(a)'
            ) % (attr, rel)
    tx.run(cmd, nameA=sro[0], nameB=sro[2])


# use these functions
def merge_party_against_party(tx, sro):
    merge_party_rel_party(tx, sro, 'IS_AGAINST')

def merge_case_plaintiff_party(tx, sro):
    merge_party_rel_case(tx, sro, 'IS_PLAINTIFF_OF')

def merge_case_defendant_party(tx, sro):
    merge_party_rel_case(tx, sro, 'IS_DEFENDANT_OF')

def merge_case_type(tx, sro):
    merge_case_rel_attr(tx, sro, 'IS_OF_TYPE', 'CourtType')

def merge_case_location(tx, sro):
    merge_case_rel_attr(tx, sro, 'TOOK_PLACE_IN', 'Location')

def merge_case_references(tx, sro):
    merge_case_rel_attr(tx, sro, 'REFERENCES', 'Case')

def merge_case_date(tx, sro):
    merge_case_rel_attr(tx, sro, 'DECIDED_ON', 'Date')

def merge_appellant(tx,sro):
    merge_party_rel(tx, sro, 'IS_APPELLANT_OF', 'Party')

def merge_appellee(tx,sro):
    merge_party_rel(tx, sro, 'IS_APPELLEE_OF', 'Party')

def merge_verdict(tx,sro):
    merge_case_rel_attr(tx, sro, 'VERDICT_IS', 'Verdict')

def merge_evidence(tx,sro):
    merge_case_rel_attr(tx, sro, 'EVIDENCE_IS', 'Evidence')

phrase_map = {
    'against': merge_party_against_party,
    'plaintiff_is': merge_case_plaintiff_party,
    'defendant_is': merge_case_defendant_party,
    'appellant_is': merge_appellant,
    'appellee_is': merge_appellee,
    'court_type': merge_case_type,
    'court_location': merge_case_location,
    'decision_date' : merge_case_date,
    'references' : merge_case_rel_attr,
    'verdict' : merge_verdict,
    'evidence' : merge_evidence
}

# (CASE_NAME, "verdict", free text)
# (CASE_NAME, "evidence", free text

# sros is a List[Tuple(Subject, Relation, Object)]
# as of git commit 0e610f060fd71b62c2784959b0f4b42b3a39c979
def fill_db(driver, sros):
    with driver.session() as sess:
        tx = sess.begin_transaction()
        for t in sros:
            relation = t[1]
            merge_func = phrase_map[relation]
            merge_func(tx, t)
        tx.commit()

hardcoded_test = [
  ('Kat',        'against',        'Ben'),
  ('Kat v. Ben', 'plaintiff',      'Kat'),
  ('Kat v. Ben', 'defendant',      'Ben'),
  ('Kat v. Ben', 'court type',     'highest'),
  ('Kat v. Ben', 'court location', 'GDC 3rd floor atrium'),
  ('Shiva',        'against',      'Hadi'),
  ('Shiva v. Hadi', 'plaintiff',      'Shiva'),
  ('Shiva v. Hadi', 'defendant',      'Hadi'),
  ('Shiva v. Hadi', 'court type',     'medium'),
  ('Shiva v. Hadi', 'court location', 'GDC 2nd floor atrium'),
  ('Ben',        'against',      'Hadi'),
  ('Ben v. Hadi', 'plaintiff',      'Ben'),
  ('Ben v. Hadi', 'defendant',      'Hadi'),
  ('Ben v. Hadi', 'court type',     'medium'),
  ('Ben v. Hadi', 'court location', 'GDC 2nd floor atrium'),
  ('Ben v. Hadi', 'references', 'Shiva v. Hadi')
 ]

def parse_shiva_triples(file):
    cases = []
    with open(file, 'r') as f:
        for line in f.readlines():
            line = line.rstrip('\n')
            line = line.split('*')
            line = line[0].split(',')
            if len(line) == 3:
                first = line[0].strip('\'').strip('\'')
                first = first[2:]
                rel = line[1]
                rel = rel[2:len(rel)-1].strip(' ')
                second = line[2]
                second = second[2:len(second)-2]
                cases.append([first,rel,second])
    return cases

if __name__ == '__main__':
    neo = CaseLawNeoDB(config.instance, config.username, config.password)
    cases = parse_shiva_triples(sys.argv[1])
    fill_db(neo.driver, cases)

    # with open(sys.argv[1], 'r') as f:
    #     for line in f.readlines():
    #         line = line.rstrip('\n')
    #         # print(line)
    #         arr = line.split('*')[:-1]
    #         # omit = ['appellant_is','decision_date','appellee_is']
    #         # if arr[1] not in omit:
    #         cases.append(arr)
    #     # print(cases)
    # fill_db(neo.driver, cases)
    # neo.close()
