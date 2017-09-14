from stream import protocol
from cache import patch
from cache import consts
import uuid


def test_retran_msg():
    uid = uuid.uuid4().hex
    key = 314159
    cid = uuid.uuid4().hex
    msg = protocol.ReqResMsg.retran(uid, key, cid)

    assert isinstance(msg, protocol.ReqResMsg)
    assert msg.cmd == consts._cmd_ret_
    assert msg.key == key
    assert msg.unique_id == uid
    assert msg.corr_id == cid


def test_retran_ack():
    cid = uuid.uuid4().hex
    msg = protocol.ReqResMsg.ack(cid)
    assert isinstance(msg, protocol.ReqResMsg)
    assert msg.cmd == consts._cmd_ack_
    assert not msg.key
    assert not msg.unique_id
    assert msg.corr_id == cid


def test_retran_nack():
    cid = uuid.uuid4().hex
    msg = protocol.ReqResMsg.nack(cid)
    assert isinstance(msg, protocol.ReqResMsg)
    assert msg.cmd == consts._cmd_nak_
    assert not msg.key
    assert not msg.unique_id
    assert msg.corr_id == cid


def test_to_network():
    uid = uuid.uuid4().hex
    key = '314159'
    cid = uuid.uuid4().hex
    msg = protocol.ReqResMsg.retran(uid, key, cid)
    buf = msg.to_network()

    for element in buf:
        assert isinstance(element, bytes)


def test_from_network():
    uid = uuid.uuid4().hex
    key = '314159'
    cid = uuid.uuid4().hex
    msg = protocol.ReqResMsg.retran(uid, key, cid)
    buf = msg.to_network()
    msg2 = protocol.ReqResMsg.from_network(buf)

    assert isinstance(msg2, protocol.ReqResMsg)
    assert msg2.cmd == consts._cmd_ret_
    assert msg2.key == key
    assert msg2.unique_id == uid
    assert msg2.corr_id == cid


def test_reqres_str_none():
    cid = '_cid_'
    msg = protocol.ReqResMsg.nack(cid)
    assert str(msg) == 'Cmd NACK uid:0x key:0x cid:0x_cid_'


def test_reqres_str_truncated():
    uid = '0123456789'
    key = '0123456789'
    cid = '0123456789'
    msg = protocol.ReqResMsg.retran(uid, key, cid)
    assert str(msg) == 'Cmd RETRAN uid:0x012345 key:0x012345 cid:0x012345'


def test_pub_msg():
    top = uuid.uuid4().hex
    cid = uuid.uuid4().hex
    pay = uuid.uuid4().hex
    msg = protocol.PubSubMsg(top, cid, pay)
    assert isinstance(msg, protocol.PubSubMsg)


def test_pubsub_to_network():
    top = uuid.uuid4().hex
    cid = uuid.uuid4().hex
    pay = uuid.uuid4().hex
    msg = protocol.PubSubMsg(top, cid, pay)
    buf = msg.to_network()
    for element in buf:
        assert isinstance(element, bytes)


def test_pubsub_from_network():
    top = uuid.uuid4().hex
    cid = uuid.uuid4().hex
    pay = uuid.uuid4().hex
    msg = protocol.PubSubMsg(top, cid, pay)
    buf = msg.to_network()
    msg2 = protocol.PubSubMsg.from_network(buf)
    assert isinstance(msg2, protocol.PubSubMsg)
    assert msg2.topic == top
    assert msg2.corr_id == cid
    assert msg2.payload == pay


def test_pubsub_str():
    top = '0123456789'
    cid = '0123456789'
    pay = '0123456789'
    msg = protocol.PubSubMsg(top, cid, pay)
    assert str(msg) == 'PubSubMsg top:0x012345 cid:0x012345 pay:0123456789'

