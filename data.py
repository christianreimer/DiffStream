"""
Generate an arbitrary datastream
"""

import uuid
import datetime
import random


_user_names = ['Alice', 'Bob', 'Charles', 'Dana', 'Eric', 'Felix', 'Gina']
_descriptions = ['Super Duper Space Monkey', 'Antique Bobble Wheel',
                 'One-of-a-kind Dinglewobber', 'Singularity Point Projector']


def auction_generator():
    """
    Generate fake auction data for testing purposes.

    Returns a generator
    """
    data = {'key': uuid.uuid4().hex,
            'description': random.choice(_descriptions),
            'last_bid': {'user': None, 'price': 0, 'time': None}}

    while True:
        yield data

        data['last_bid'] = \
            {'user': random.choice(_user_names),
             'price': data['last_bid']['price'] + random.randint(1, 10),
             'time': str(datetime.datetime.utcnow())}
