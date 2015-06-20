import json, redis, pickle
from os import environ

REDIS_URL = environ['REDIS_URL']

r = redis.from_url(REDIS_URL)
r.flushdb()
o = open('fixture.json', 'r')
contents = o.read()
j = json.loads(contents)
for card in j:
    id = card['id']
    pickled = pickle.dumps(card)
    r.set(id, pickled)
