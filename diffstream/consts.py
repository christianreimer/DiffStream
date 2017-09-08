"""
Constants used to coordinate communication
"""

_role_producer_ = '_producer_'
_role_consumer_ = '_consumer_'

_cmd_upd_ = 'u'
_cmd_new_ = 'n'
_cmd_del_ = 'd'
_cmd_ret_ = 'r'


cmd_name = {_cmd_upd_: 'UPDATE',
            _cmd_new_: 'NEW',
            _cmd_del_: 'DELETE',
            _cmd_ret_: 'RETRAN'}
