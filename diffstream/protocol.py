"""
Classes and constants to assist with the IPC protocol.
"""
import uuid
from . import consts


class ReqResCmd(object):
    def __init__(self, cmd, unique_id='', key='', corr_id=''):
        self.cmd = cmd
        self.unique_id = unique_id
        self.key = key
        self.corr_id = corr_id

    @classmethod
    def retran(cls, unique_id, key, corr_id=None):
        """
        Construct RETRAN Request Resonse Command
        """
        _u = isinstance(unique_id, bytes) and unique_id.decode() or unique_id
        _k = isinstance(key, bytes) and key.decode() or key
        _c = corr_id or uuid.uuid4().hex
        _c = isinstance(_c, bytes) and _c.decode() or _c
        return ReqResCmd(consts._cmd_ret_, _u, _k, _c)

    @classmethod
    def ack(cls, corr_id):
        """
        Construct ACK Request Response Command
        """
        return ReqResCmd(consts._cmd_ack_, corr_id=corr_id)

    @classmethod
    def nack(cls, corr_id):
        """
        Construct NACK Request Response Command
        """
        return ReqResCmd(consts._cmd_nak_, corr_id=corr_id)

    @classmethod
    def from_network(cls, buffer):
        """
        Convert zmq message buffer into ReqResCmd object.ReqResCmd
        """
        cmd = buffer[0].decode()
        unique_id = buffer[1].decode()
        key = buffer[2].decode()
        corr_id = buffer[3].decode()
        return ReqResCmd(cmd, unique_id, key, corr_id)

    def to_network(self):
        """
        Return encoded representation suitable for transmission via zmq.
        """
        cmd = isinstance(self.cmd, bytes) and self.cmd or self.cmd.encode()
        key = isinstance(self.key, bytes) and self.key or self.key.encode()

        return (cmd,
                self.unique_id.encode(),
                key,
                self.corr_id.encode())

    def __str__(self):
        return 'Cmd {} uid:0x{} key:0x{} cid:0x{}'.format(
            consts.cmd_name[self.cmd],
            self.unique_id[:6],
            self.key[:6],
            self.corr_id[:6])


class PubSubBuf(object):
    def __init__(self, topic, corr_id, payload):
        self.topic = topic
        self.corr_id = corr_id
        self.payload = payload

    @classmethod
    def from_network(cls, buf):
        _t = buf[0].decode()
        _c = buf[1].decode()
        _p = buf[2].decode()
        return PubSubBuf(_t, _c, _p)

    def to_network(self):
        return (self.topic.encode(),
                self.corr_id.encode(),
                self.payload.encode())

    def __str__(self):
        return 'PubSubBuf top:0x{} cid:0x{} pay:{}'.format(
            self.topic[:6],
            self.corr_id[:6],
            str(self.payload))
