"""
DiffCache

A DiffCache provides a simply interface for transmitting a stream of python
dicts, where each messages applears to contain the entire state of the dict,
but only the difference is transmitted in each message.

This is achieve by keeping a cache on both the sending and the receiving side.
One the sending side, each dict is diffed against its previous state and only
the changes are transmitted. On the receiving side, each diff is applied to
the previous state to arrive at the new state.

A checksum is included with each message so that the receiver can validate the
derived state to ensure the two parties are in sych. In case of checksum
mismatch, the receiver can request a full retansmission from the sender to sych
state.

Using a DiffCache can produce significant bandwidth savings when transmitting
objects where a subset of the keys are ubdated frequently, while the rest are
never or rarely updated. This is achieved while allowing both sender and
receiver to operate as if the entire dict is sent with every message.


Example:

>>> from diffstream import cache
>>>
>>> producer = cache.DiffCache.producer()
>>> consumer = cache.DiffCache.consumer()
>>>
>>> data = {'key': 314159, 'a': 'Some really, really important text', 'b': 42,
            'c': {'c1': True, 'c2': False}, 'd': list(range(10))}
>>> pprint.pprint(data)
{'a': 'Some really, really important text',
 'b': 42,
 'c': {'c1': True, 'c2': False},
 'd': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
 'key': 314159}
>>>
>>> msg = producer.update(data)
>>> _, _, data_ = consumer.update(msg)
>>> pprint.pprint(data_)
{'a': 'Some really, really important text',
 'b': 42,
 'c': {'c1': True, 'c2': False},
 'd': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
 'key': 314159}
>>>
>>> data['c']['c3'] = 'Maybe'
>>> pprint.pprint(data)
{'a': 'Some really, really important text',
 'b': 42,
 'c': {'c1': True, 'c2': False, 'c3': 'Maybe'},
 'd': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
 'key': 314159}
>>>
>>> msg = producer.update(data)
>>> _, _, data_ = consumer.update(msg)
>>> pprint.pprint(data_)
{'a': 'Some really, really important text',
 'b': 42,
 'c': {'c1': True, 'c2': False, 'c3': 'Maybe'},
 'd': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
 'key': 314159}
>>>
>>> buf = json.dumps(data).encode()
>>> type(buf), len(buf)
(<class 'bytes'>, 151)
>>> buf_ = msg.encode()
>>> type(buf_), len(buf_)
(<class 'bytes'>, 115)
"""


class ChecksumMismatchError(Exception):
    """
    Checksum validation failed when trying to apply an update. A
    retransmission should be requested to sync the state
    """
    pass


class PatchMissmatchError(Exception):
    """
    The JSON patch could not be applied. A retransmission should be
    requested to sync the state
    """
    pass


class CacheKeyError(Exception):
    """
    The cache could not be updated because no existing object was found
    for the specified key. A retransmission should be requested to sync the
    state
    """
    pass


class CacheKeyWarning(Exception):
    """
    An object could not be deleted from the cache because no existing object
    was found for the specified key. No further actions are required to sync
    the state
    """
    pass

