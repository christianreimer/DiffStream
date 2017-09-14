"""

"""

from . import consts

import json
import jsonpatch


class DataMsg(object):
    """DataMsg to a cached object"""

    def __init__(self, cmd, key, data, checksum):
        self.cmd = cmd
        self.key = key
        self.data = data
        self.checksum = checksum

    @classmethod
    def new_data(cls, key, data):
        return DataMsg(consts._cmd_new_, key, data, None)

    @classmethod
    def upd_data(cls, key, data, checksum):
        return DataMsg(consts._cmd_upd_, key, data, checksum)

    @classmethod
    def del_data(cls, key):
        return DataMsg(consts._cmd_del_, key, None, None)

    @classmethod
    def ret_data(cls, key, data):
        return DataMsg(consts._cmd_ret_, key, data, None)

    @classmethod
    def from_json(cls, json_str):
        cmd, key, data, checksum = json.loads(json_str)
        if isinstance(data, str) and cmd == consts._cmd_upd_:
            data = jsonpatch.JsonPatch.from_string(data)
        return DataMsg(cmd, key, data, checksum)

    def to_json(self):
        data = self.data
        if self.data and isinstance(self.data, jsonpatch.JsonPatch):
            data = self.data.to_string()
        return json.dumps([self.cmd, self.key, data, self.checksum])

    def encode(self):
        return self.to_json().encode()

    def __eq__(self, other):
        if not (self.cmd == other.cmd and
                self.key == other.key and
                self.checksum == other.checksum and
                type(self.data) == type(other.data)):  # noqa
            return False

        if isinstance(self.data, dict):
            return json.dumps(self.data) == json.dumps(other.data)

        if isinstance(self.data, jsonpatch.JsonPatch):
            return self.data.to_string() == other.data.to_string()

        return self.data == other.data

    def __str__(self):
        data_str = str(self.data)
        out_str = data_str[:40]

        return 'DataMsg cmd:{} key:{} data:{}{}'.format(
            consts.cmd_name[self.cmd],
            self.key,
            out_str,
            (len(data_str) > len(out_str) and '...' or ''))
