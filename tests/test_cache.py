import hashlib
import json
import pytest

from cache import cache
from cache import ChecksumMismatchError
from cache import PatchMissmatchError
from cache import CacheKeyError
from cache import CacheKeyWarning


def create_caches():
    producer = cache.DiffCache.producer()
    consumer = cache.DiffCache.consumer()
    return producer, consumer


def test_bad_cache_role():
    with pytest.raises(ValueError):
        cache.DiffCache(role='Something that does not exist')


def dicts_are_equal(d1, d2):
    return hashlib.md5(json.dumps(d1).encode()).hexdigest() == \
        hashlib.md5(json.dumps(d2).encode()).hexdigest()


def test_new_data_object():
    producer, consumer = create_caches()
    key = 314159
    data = {'a': 1, 'b': 2, 'key': key}
    msg = producer.update(data)
    _, _, data_ = consumer.update(msg)
    assert dicts_are_equal(data, data_)


def test_upd_data_elememnt():
    producer, consumer = create_caches()
    key = 314159
    data = {'a': 1, 'b': 2, 'key': key}
    msg = producer.update(data)
    consumer.update(msg)
    data['a'] = 3
    msg = producer.update(data)
    _, _, data_ = consumer.update(msg)
    assert dicts_are_equal(data, data_)


def test_add_data_element():
    producer, consumer = create_caches()
    key = 314159
    data = {'a': 1, 'b': 2, 'key': key}
    msg = producer.update(data)
    consumer.update(msg)
    data['c'] = 3
    msg = producer.update(data)
    _, _, data_ = consumer.update(msg)
    assert dicts_are_equal(data, data_)


def test_del_data_element():
    producer, consumer = create_caches()
    key = 314159
    data = {'a': 1, 'b': 2, 'key': key}
    msg = producer.update(data)
    consumer.update(msg)
    del data['a']
    msg = producer.update(data)
    _, _, data_ = consumer.update(msg)
    assert dicts_are_equal(data, data_)


def test_del_data_object():
    producer, consumer = create_caches()
    key = 314159
    data = {'a': 1, 'b': 2, 'key': key}
    msg = producer.update(data)
    assert key in producer
    consumer.update(msg)
    assert key in producer
    msg = producer.delete(key)
    assert key not in producer
    consumer.update(msg)
    assert key not in consumer


def test_dict_likeness_len():
    producer, consumer = create_caches()
    key = 314159
    data = {'a': 1, 'b': 2, 'key': key}
    assert len(producer) == len(consumer) == 0
    consumer.update(producer.update(data))
    assert len(producer) == len(consumer) == 1
    consumer.update(producer.delete(key))
    assert len(producer) == len(consumer) == 0


def test_dict_likeness_contains():
    producer, consumer = create_caches()
    key = 314159
    data = {'a': 1, 'b': 2, 'key': key}
    assert key not in producer
    assert key not in consumer
    consumer.update(producer.update(data))
    assert key in producer
    assert key in consumer
    consumer.update(producer.delete(key))
    assert key not in producer
    assert key not in consumer


def test_dict_likeness_getattr():
    producer, _ = create_caches()
    key = 314159
    data = {'a': 1, 'b': 2, 'key': key}
    producer.update(data)
    data2 = producer[key]
    assert (data['key'] == data2['key'] and
            data['a'] == data2['a'])

def test_dict_likeness_get():
    producer, _ = create_caches()
    assert not producer.get('NonExistingKey', None)


def test_checksum_mismatch_exception():
    producer, consumer = create_caches()
    key = 314159
    data = {'a': 1, 'b': 2, 'key': key}
    consumer.update(producer.update(data))
    data['a'] = 2
    msg = producer.update(data)
    msg.checksum = 123
    with pytest.raises(ChecksumMismatchError):
        consumer.update(msg)


def test_patch_mismatch_exception():
    producer, consumer = create_caches()
    key = 314159
    data = {'a': 1, 'b': 2, 'key': key}
    consumer.update(producer.update(data))
    data['c'] = 1
    producer.update(data)
    data['c'] = 2
    with pytest.raises(PatchMissmatchError):
        consumer.update(producer.update(data))


def test_no_key_exception():
    producer = cache.DiffCache.producer()
    data = {'a': 1, 'b': 2}
    with pytest.raises(KeyError):
        producer.update(data)


def test_cache_key_exception():
    producer, consumer = create_caches()
    key = 314159
    data = {'a': 1, 'b': 2, 'key': key}
    producer.update(data)
    data['c'] = 1
    with pytest.raises(CacheKeyError):
        consumer.update(producer.update(data))


def test_cache_key_warning():
    producer, consumer = create_caches()
    key = 314159
    data = {'a': 1, 'b': 2, 'key': key}
    producer.update(data)
    with pytest.raises(CacheKeyWarning):
        consumer.update(producer.delete(key))


def test_delete_consumer_key_exception():
    producer, _ = create_caches()
    key = 314159
    data = {'a': 1, 'b': 2, 'key': key}
    producer.update(data)
    with pytest.raises(KeyError):
        producer.delete(key + 1)


def test_invalid_command_exception():
    producer, consumer = create_caches()
    key = 314159
    data = {'a': 1, 'b': 2, 'key': key}
    msg = producer.update(data)
    msg.cmd = 'bad command'
    with pytest.raises(ValueError):
        consumer.update(msg)


def test_retran_key_exception():
    producer = cache.DiffCache.producer()
    with pytest.raises(KeyError):
        producer.retran('KeyThatDoesNotExist')


def test_no_copy():
    producer = cache.DiffCache.producer(copyobj=False)
    key = 314159
    data = {'a': 1, 'b': 2, 'key': key}
    producer.update(data)
    data['a'] = 3
    data_ = producer[key]
    assert data_['a'] == data['a']


def test_strict_diff():
    producer = cache.DiffCache.producer(strict=True)
    key = 314159
    data = {'a': 1, 'b': 2, 'key': key}
    producer.update(data)
    with pytest.raises(ValueError):
        producer.update(data)


def test_to_str():
    producer, consumer = create_caches()
    assert 'DiffCache _producer_' == str(producer)
    assert 'DiffCache _consumer_' == str(consumer)


def test_retran_with_byte_key():
    producer = cache.DiffCache.producer()
    key = 'MyKey'
    data = {'key': key, 'a': 1}
    producer.update(data)
    producer.retran(key.encode())

