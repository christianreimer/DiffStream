
from stream import stats
import json


def test_track_nothing_empty():
    s = stats.UtilizationStats()
    s.transmitted(123, 'Something')
    assert not s.bytes_xmited
    assert not s.bytes_original
    assert not s.num_messages
    assert not s.messages_types
    assert not s.unique_keys


def test_transmitted():
    s = stats.UtilizationStats(track_bytes=True)
    data = {'a': 1, 'b': 'Hello'}
    s.transmitted(123, data)
    s.transmitted(234, data)
    assert s.bytes_xmited == (123 + 234)
    assert s.bytes_original == 2 * len(json.dumps(data).encode())


def test_messages():
    s = stats.UtilizationStats(track_messages=True)
    s.transmitted(0, '', cmd='SomeCommand')
    s.transmitted(0, '', cmd='SomeCommand')
    assert s.num_messages == 2
    assert not set(s.messages_types.items()) - set([('SomeCommand', 2)])


def test_keys():
    s = stats.UtilizationStats(track_keys=True)
    s.transmitted(0, '', '', 314159)
    s.transmitted(0, '', '', 314159)
    s.transmitted(0, '', '', 271828)
    assert len(s.unique_keys) == 2
