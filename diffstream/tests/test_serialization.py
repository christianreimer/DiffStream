from diffstream import cache
from diffstream import consts


def create_caches():
    producer = cache.DiffCache(consts._role_producer_)
    consumer = cache.DiffCache(consts._role_consumer_)
    return producer, consumer


def test_to_from_json_new():
    producer, _ = create_caches()
    key = 314159
    data = {'a': 1, 'b': 2, 'key': key}
    msg1 = producer.update(data)
    msg2 = cache.DataMsg.from_json(msg1.to_json())
    assert isinstance(msg1, cache.DataMsg)
    assert isinstance(msg2, cache.DataMsg)
    assert msg1 == msg2


def test_to_from_json_ret():
    producer, _ = create_caches()
    key = 314159
    data = {'a': 1, 'b': 2, 'key': key}
    producer.update(data)
    msg1 = producer.retran(key)
    msg2 = cache.DataMsg.from_json(msg1.to_json())
    assert isinstance(msg1, cache.DataMsg)
    assert isinstance(msg2, cache.DataMsg)
    assert msg1 == msg2


def test_to_from_json_upd():
    producer, _ = create_caches()
    key = 314159
    data = {'a': 1, 'b': 2, 'key': key}
    producer.update(data)
    data['a'] = 2
    msg1 = producer.update(data)
    assert msg1.cmd == consts._cmd_upd_
    msg2 = cache.DataMsg.from_json(msg1.to_json())
    assert isinstance(msg1, cache.DataMsg)
    assert isinstance(msg2, cache.DataMsg)
    assert msg1 == msg2


def test_to_from_json_del():
    producer, _ = create_caches()
    key = 314159
    data = {'a': 1, 'b': 2, 'key': key}
    producer.update(data)
    msg1 = producer.delete(key)
    msg2 = cache.DataMsg.from_json(msg1.to_json())
    assert msg1 == msg2


def test_to_from_json_bad():
    producer, _ = create_caches()
    key = 314159
    data = {'a': 1, 'b': 2, 'key': key}
    msg1 = producer.update(data)
    msg2 = cache.DataMsg.from_json(msg1.to_json())
    msg2.key = 314
    assert not msg1 == msg2


def test_encode():
    producer, _ = create_caches()
    key = 314159
    data = {'a': 1, 'b': 2, 'key': key}
    msg = producer.update(data)
    byte_str = msg.encode()
    assert isinstance(byte_str, bytes)


def test_str():
    producer, _ = create_caches()
    key = 314
    data = {'a': 1, 'b': 2, 'key': key}
    msg = producer.update(data)
    assert str(msg) == \
        "DataMsg cmd:NEW key:314 data:{'a': 1, 'b': 2, 'key': 314}"
