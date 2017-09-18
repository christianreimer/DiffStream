"""
DiffCache
"""

import copy
import hashlib
import json
import jsonpatch
import collections
from . import consts
from . import patch
from . import ChecksumMismatchError
from . import PatchMissmatchError
from . import CacheKeyError
from . import CacheKeyWarning


def md5_checksum(data):
    """
    md5 hash (as hex) of the json encoded data.
    """
    return hashlib.md5(json.dumps(data).encode('utf-8')).hexdigest()


class DiffCache(object):
    """DiffCache"""

    def __init__(self, role, key_name='key', copyobj=True, strict=False):
        if role not in (consts._role_producer_, consts._role_consumer_):
            raise ValueError('Invalid role {}'.format(role))

        if role == consts._role_producer_:
            self.update = self._update_producer
            self.delete = self._delete_producer
            self.retran = self._retran_producer
        else:
            self.update = self._update_consumer

        self.role = role
        self.data_store = {}
        self.key_name = key_name
        self.copyobj = copyobj
        self.strict = strict
        self.stats = collections.Counter()

    @classmethod
    def producer(cls, key_name='key', copyobj=True, strict=False):
        """
        Create a producer cache.
        """
        return DiffCache(consts._role_producer_, key_name, copyobj, strict)

    @classmethod
    def consumer(cls, key_name='key', copyobj=True, strict=False):
        """
        Create a consumer cache.
        """
        return DiffCache(consts._role_consumer_, key_name, copyobj, strict)

    def __getitem__(self, key):
        return self.data_store[key]

    def get(self, key, default_value):
        return self.data_store.get(key, default_value)

    def __contains__(self, key):
        return key in self.data_store

    def __len__(self):
        return len(self.data_store)

    def __str__(self):
        return 'DiffCache {}'.format(self.role)

    def update(self):
        raise NotImplementedError  # pragma: no cover

    def delete(self):
        raise NotImplementedError  # pragma: no cover

    def retran(self):
        raise NotImplementedError  # pragma: no cover

    def _maybe_copy(self, data):
        """
        Perform a deep copy of data if cache is configured for it.
        """
        if self.copyobj:
            return copy.deepcopy(data)
        else:
            return data

    def _update_producer(self, data_new):
        """
        Update local cache and create a diff describing the update.
        """
        try:
            key = data_new[self.key_name]
        except KeyError:
            raise KeyError('Could not find data using keyname `{}`'.format(
                self.key_name))

        data_old = self.data_store.get(key, {})
        self.data_store[key] = self._maybe_copy(data_new)

        if data_old:
            diff = jsonpatch.make_patch(data_old, data_new)
            if self.strict and not diff:
                raise ValueError('Non diff update attempted')
            checksum = md5_checksum(data_new)
            return patch.DataMsg.upd_data(key, diff, checksum)
        else:
            return patch.DataMsg.new_data(key, data_new)

    def _delete_producer(self, key):
        """
        Delete the given key from the cache.
        """
        try:
            del self.data_store[key]
        except KeyError:
            raise KeyError('Could not find data using key {}={}'.format(
                self.key_name, key))
        return patch.DataMsg.del_data(key)

    def _retran_producer(self, key):
        """
        Send a retransmission for the given key.
        """
        if isinstance(key, bytes):
            key = key.decode()

        try:
            return patch.DataMsg.ret_data(key, self.data_store[key])
        except KeyError:
            raise KeyError('Could not find data using key {}={}'.format(
                self.key_name, key))

    def _update_consumer(self, data_msg):
        """
        Update consumer cache with the received data message.
        """
        cmd = data_msg.cmd
        key = data_msg.key
        data = data_msg.data
        checksum = data_msg.checksum

        self.stats[cmd] += 1

        if cmd in (consts._cmd_new_, consts._cmd_ret_):
            # This is a new data object or a retansmission of existing data,
            # simply insert/override
            self.data_store[key] = self._maybe_copy(data)

        elif cmd == consts._cmd_upd_:
            # This is a data update, need to update the existing data object
            # and check for validity
            try:
                data_old = self.data_store[key]
            except KeyError:
                # This will happen if the _msg_new_ was missed
                raise CacheKeyError(
                    'Could not find existing entry for key {}'.format(key))

            # if isinstance(data, str):
            #     patch = jsonpatch.JsonPatch.from_string(data)
            # else:
            patch = data

            try:
                data = patch.apply(data_old)
            except jsonpatch.JsonPatchConflict:
                # jsonpointer.JsonPointerException
                # json.decoder.JSONDecodeError
                # This can happen when we get an update for an object where we
                # do not have the correct current state.
                raise PatchMissmatchError(
                    'Could not apply update for key {}'.format(key))

            if not md5_checksum(data) == checksum:
                raise ChecksumMismatchError(
                    'Checksum mismatch after update to {} '
                    '(discarding update)'.format(key))

            self.data_store[key] = data

        elif cmd == consts._cmd_del_:
            # This is a delete command, simply remove the data object
            try:
                del self.data_store[key]
            except KeyError:
                # This can happen when we get a delete for an object where we
                # missed the _cmd_new_
                raise CacheKeyWarning(
                    'Could not find existing entry for key'.format(key))

        else:
            raise ValueError('Invalid command {} received'.format(cmd))

        return cmd, key, data
