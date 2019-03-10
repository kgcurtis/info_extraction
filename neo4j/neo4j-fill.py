from neo4j import GraphDatabase, basic_auth
import config

class CaseLawNeoDB(object):
    def __init__(self, uri, user, pw):
        creds = basic_auth(user, pw)
        self.driver = GraphDatabase.driver(uri, auth=creds) 

    def close(self):
        self.driver.close()

# auto-commit based node creation
def merge_person(driver, name):
    cmd = 'MERGE (p:Person {name:$name})'
    with driver.session() as sess:
        return sess.run(cmd, name=name)

# transaction based node creation
def create_brick(driver, c, l, w, h):
    with driver.session() as sess:
        tx = sess.begin_transaction()
        bid = create_brick_node(tx, c)
        res = set_brick_dims(tx, bid, l, w, h)
        print(res)
        tx.commit()

def create_brick_node(tx, c):
    cmd = 'CREATE (b:Brick {color:$color}) RETURN id(b)'
    return tx.run(cmd, color=c).single().value()


def set_brick_dims(tx, bid, l, w, h):
    cmd = ('MATCH (b:Brick) WHERE id(b) = $bid '
        'SET b.length = $length '
        'SET b.width = $width '
        'SET b.height = $height'
    )
    return tx.run(cmd, bid = bid, length=l, width=w, height=h)

# auto-commit based relationship creation
def create_person_owned_colored_bricks(driver, name, color):
    cmd = (
        'MATCH (p:Person {name:$name}),(b:Brick {color:$color}) '
        'MERGE (p)-[:OWNED]->(b)'
    )
    with driver.session() as sess:
        tx = sess.begin_transaction()
        tx.run(cmd, name=name, color=color)
        tx.commit()

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


phrase_map = {
    'against': merge_party_against_party,
    'plaintiff': merge_case_plaintiff_party,
    'defendant': merge_case_defendant_party,
    'court type': merge_case_type,
    'court location': merge_case_location
}

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
 ]

if __name__ == '__main__':
    neo = CaseLawNeoDB(config.instance, config.username, config.password)
    fill_db(neo.driver, hardcoded_test)
    neo.close()
