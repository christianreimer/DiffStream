"""
Measuring the stats releated to bytes sent/received as well as messages
processed.
"""

import collections
import copy
import json


class UtilizationStats(object):
    """Stats about bandwidth used"""
    def __init__(self, **kwargs):
        self.track_bytes = kwargs.get('track_bytes', False)
        self.track_messages = kwargs.get('track_messages', False)
        self.track_keys = kwargs.get('track_keys', False)

        self.stats = {
            'bytes_xmited': 0,
            'bytes_original': 0,
            'num_messages': 0,
            'messages_types': collections.defaultdict(int),
            'unique_keys': set()}

        self.report_interval = kwargs.get('report_interval', None)
        self.stats_lst = []

    def __str__(self):
        return str(self.stats)  # pragma: no cover

    def transmitted(self, bytes_sent, original='', cmd=None, key=None):
        self.stats['num_messages'] += 1

        if self.track_bytes:
            self.stats['bytes_xmited'] += bytes_sent
            self.stats['bytes_original'] += len(json.dumps(original).encode())
        if self.track_messages:
            self.stats['messages_types'][cmd] += 1
        if self.track_keys:
            self.stats['unique_keys'].add(key)
        self._report()

    def _report(self):
        if not self.report_interval or \
                (self.stats['num_messages'] % self.report_interval):
            return
        self.stats_lst.append(copy.deepcopy(self.stats))

    def report(self):
        return self.stats_lst

