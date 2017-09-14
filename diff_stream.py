#! /usr/bin/env python

"""
DiffStream Runner

Simple application to perform sample runs of the DiffCache/DiffStream
application.

Usage:
  diff_stream.py server
  diff_stream.py client

Options:
  -h --help     Show this screen.
"""

from docopt import docopt
from app import client
from app import server


if __name__ == '__main__':
    args = docopt(__doc__)

    if args['client']:
        client.main()
    elif args['server']:
        server.main()
