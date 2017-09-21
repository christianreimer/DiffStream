"""
Measuring the stats releated to bytes sent/received as well as messages
processed.
"""

import collections
import json


class UtilizationStats(object):
    """Stats about bandwidth used"""
    def __init__(self, **kwargs):
        self.track_bytes = kwargs.get('track_bytes', False)
        self.track_messages = kwargs.get('track_messages', False)
        self.track_keys = kwargs.get('track_keys', False)

        self.bytes_xmited = 0
        self.bytes_original = 0
        self.num_messages = 0
        self.messages_types = collections.defaultdict(int)
        self.unique_keys = set()

    def __str__(self):
        return '\n'.join(  # pragma: no cover
            ['Bytes Xmited:   {}'.format(self.bytes_xmited),
             'Bytes original: {}'.format(self.bytes_original),
             'Num Messages:   {}'.format(self.num_messages),
             'Message Types:  {}'.format(self.messages_types),
             'Uniue Keys:     {}'.format(len(self.unique_keys))])

    def transmitted(self, bytes_sent, original='', cmd=None, key=None):
        if self.track_bytes:
            self.bytes_xmited += bytes_sent
            self.bytes_original += len(json.dumps(original).encode())
        if self.track_messages:
            self.num_messages += 1
            self.messages_types[cmd] += 1
        if self.track_keys:
            self.unique_keys.add(key)
