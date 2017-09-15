"""
Generate an arbitrary datastream
"""

import uuid
import datetime
import random


_user_names = ['Alice',
               'Bob',
               'Charles',
               'Dana',
               'Eric',
               'Felix',
               'Gina',
               'Helen',
               'Ina',
               'Josie',
               'Kenny',
               'Lars',
               'Michelle',
               'Nicholas',
               'Oscar',
               'Pepper']

_titles = ['Super Duper Space Monkey',
           'Antique Bobble Wheel',
           'One-of-a-kind Dinglewobber',
           'Singularity Point Projector',
           'Yesterdays Must-Have-Thing',
           'Somebody elses idea of fun']

_lorem = """Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do
 eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim
 veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea
 commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit
 esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat
 non proident, sunt in culpa qui officia deserunt mollit anim id est laborum"""


def slizer(txt):
    """
    Return a slice of the text
    """
    _l = len(txt)
    _f = random.randint(0, _l // 2)
    _t = random.randint(_f, _l)
    return _lorem[_f: _t].replace('\n', '')


def auction_generator():
    """
    Generate fake auction data for testing purposes
    """
    data = {'key': uuid.uuid4().hex,
            'tile': random.choice(_titles),
            'description': slizer(_lorem),
            'last_bid': {'user': None, 'price': 0, 'time': None}}

    while True:
        yield data

        data['last_bid'] = \
            {'user': random.choice(_user_names),
             'price': data['last_bid']['price'] + random.randint(1, 10),
             'time': str(datetime.datetime.utcnow())}
