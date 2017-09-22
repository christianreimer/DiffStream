
from stream import stats
import json


def test_track_nothing_empty():
    s = stats.UtilizationStats()
    s.transmitted(123, 'Something')
    assert s.stats['num_messages']
    assert not s.stats['bytes_xmited']
    assert not s.stats['bytes_original']
    assert not s.stats['messages_types']
    assert not s.stats['unique_keys']


def test_transmitted():
    s = stats.UtilizationStats(track_bytes=True)
    data = {'a': 1, 'b': 'Hello'}
    s.transmitted(123, data)
    s.transmitted(234, data)
    assert s.stats['bytes_xmited'] == (123 + 234)
    assert s.stats['bytes_original'] == 2 * len(json.dumps(data).encode())


def test_messages():
    s = stats.UtilizationStats(track_messages=True)
    s.transmitted(0, '', cmd='SomeCommand')
    s.transmitted(0, '', cmd='SomeCommand')
    assert s.stats['num_messages'] == 2
    assert not set(s.stats['messages_types'].items()) - \
        set([('SomeCommand', 2)])


def test_keys():
    s = stats.UtilizationStats(track_keys=True)
    s.transmitted(0, '', '', 314159)
    s.transmitted(0, '', '', 314159)
    s.transmitted(0, '', '', 271828)
    assert len(s.stats['unique_keys']) == 2


def test_dummy_report():
    s = stats.UtilizationStats(track_keys=True, report_interval=1)
    s.transmitted(0, '')
    assert isinstance(s.stats_lst, list)

