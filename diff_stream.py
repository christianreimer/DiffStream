#! /usr/bin/env python

"""
DiffStream Runner

Simple application to perform sample runs of the DiffCache/DiffStream
application.

Usage:
  diff_stream.py server|client [--pubsub=p] [--reqres=p] [--topic=t]
  diff_stream.py client [--addr=a] [--fuzz=f]
  diff_stream.py server [--sleep=s] [--count=c]

Options:
  --pubsub=p   Port # for pub sub communication [default: 5556]
  --reqres=p   Port # for req res communication [default: 5557]
  --topic=t    Pubsub topic [default: _a_topic_]
  --addr=a     Address where the server is running [default: localhost]
  --fuzz=f     Rate of failures (in %) [default: 5]
  --sleep=s    Sleep between published messages (in sec) [default: 1]
  --count=c    Number of messeges generated [default: 100]
  --help       Show this message
"""

from docopt import docopt
from app import client
from app import server


if __name__ == '__main__':
    args = docopt(__doc__)
    print(args)
    topic = args['--topic']
    pubsub = int(args['--pubsub'])
    reqres = int(args['--reqres'])

    if args['client']:
        client.start(args['--addr'], pubsub, reqres, topic)

    elif args['server']:
        server.start(pubsub, reqres, topic)
