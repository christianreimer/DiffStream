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

>>> dc_sender = DiffCache()
>>> data = {'a': 1,
            'b': {'aa': 11, 'bb': 22},
            'c': True,
            'd': 'hello',
            'uid': 1234}
>>> diff = dc_sender.diff(data)
>>>
>>> dc_receiver = DiffCache()
>>> data_copy = dc_receiver.update(diff)
>>> print(data_copy)
{'a': 1, 'b': {'aa': 11, 'bb': 22}, 'c': True, 'd': 'hello', 'uid': 1234}
>>>
>>> data['a'] = 2
>>> data['b']['aa'] = 111
>>> del data['c']
>>> data['e'] = 3.14159
>>> print(data)
{'a': 2, 'b': {'aa': 111, 'bb': 22}, 'd': 'hello', 'e': 3.14159}
>>> diff = dc_sender.diff(data)
>>>
>>> data_copy = dc_receiver.update(diff)
>>> print(data_copy)
{'a': 2, 'b': {'aa': 111, 'bb': 22}, 'd': 'hello', 'e': 3.14159}
>>>

differ.diff(d1, d2)
differ.patch(d1, diffject)
differ.validate(d1, diffject)

DiffCache(differ)
DiffStream(DiffCache)

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

