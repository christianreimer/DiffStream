from app import data
import types


def test_data_generator():
    gen = data.auction_generator()
    assert isinstance(gen, types.GeneratorType)


def test_data_create():
    gen = data.auction_generator()
    item = gen.__next__()
    assert item['title'] in data._titles
    assert not item['last_bid']['user']


def test_data_update():
    gen = data.auction_generator()
    item = gen.__next__()
    item = gen.__next__()
    assert item['title'] in data._titles
    assert item['last_bid']['user'] in data._user_names
    assert item['last_bid']['price'] > 0
