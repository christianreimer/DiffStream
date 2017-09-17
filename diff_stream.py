#! /usr/bin/env python

"""
DiffStream Runner

Simple application to perform sample runs of the DiffCache/DiffStream
application. This application creates an auction server which is sending out
updates for items as the bigs change, and a server which is receiving the item
updates. The client is applying the changes received to the internal cache to
keep it in sync with the server.


Usage:
  diff_stream.py server|client [--pubsub=p] [--reqres=p] [--topic=t]
  diff_stream.py client [--addr=a] [--fuzz=f]
  diff_stream.py server [--sleep=s] [--auctions=c] [--count=c]

Options:
  --pubsub=p    Port # for pub sub communication [default: 5556]
  --reqres=p    Port # for req res communication [default: 5557]
  --topic=t     Pubsub topic [default: _a_topic_]
  --addr=a      Address where the server is running [default: localhost]
  --fuzz=f      Failure rate [default: 0.05]
  --sleep=s     Sleep between published messages (in sec) [default: 1]
  --auctions=a  Number of auction items being run [default: 1]
  --count=c     Number of messages generated [default: 100]
  --help        Show this message
"""

from docopt import docopt
from app import client
from app import server


if __name__ == '__main__':
    args = docopt(__doc__)
    # print(args)

    addr = args['--addr']
    topic = args['--topic']
    pubsub = int(args['--pubsub'])
    reqres = int(args['--reqres'])

    if args['client']:
        client.start(addr, pubsub, reqres, topic,
                     fuzz=float(args['--fuzz']))

    elif args['server']:
        server.start(pubsub, reqres, topic,
                     sleep=float(args['--sleep']),
                     auctions=int(args['--auctions']),
                     count=int(args['--count']))
