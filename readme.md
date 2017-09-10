# DiffStream

Project to examing performance and reliability of keeping multiple distributed 
caches in sycn by sending diffs instead of the full object on each update.

## Example
```python
>>> from diffstream import cache
>>> import pprint, json
>>>
```
Create the producer and consumer caches and some data in a dict
```python
>>> producer = cache.DiffCache.producer()
>>> consumer = cache.DiffCache.consumer()
>>>
>>> data = {'key': 314159,
            'a': 'Some really, really important text',
            'b': 42,
            'c': {'c1': True, 'c2': False},
            'd': list(range(10))}
>>> pprint.pprint(data)
{'a': 'Some really, really important text',
 'b': 42,
 'c': {'c1': True, 'c2': False},
 'd': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
 'key': 314159}
>>>
```
Updating the producer cache will produce a `DataMsg` which can be applied to
the consumer cache to bring it up to date.
```python
>>> msg = producer.update(data)
>>> _, _, data_ = consumer.update(msg)
>>> pprint.pprint(data_)
{'a': 'Some really, really important text',
 'b': 42,
 'c': {'c1': True, 'c2': False},
 'd': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
 'key': 314159}
>>>
```
When changs are made to the date, subsequent `DataMsg` update will only contain
the diff needed to sync the cached dicts.
```python
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
```
Why go though the rouble with the diff? To avoid sending all of the dict data
when only a subset is changed.
```python
>>> len(json.dumps(data).encode())
len(json.dumps(data))
151
>>> len(msg.encode())
115
>>>
```
