#! /usr/bin/env python

"""
DiffStream Runner

Simple application to perform sample runs of the DiffCache/DiffStream
application. This application creates an auction server which is sending out
updates for items as the bigs change, and a server which is receiving the item
updates. The client is applying the changes received to the internal cache to
keep it in sync with the server.


Usage:
  diff_stream.py server [-p=p -r=p -t=t -n=f -s=s -u=a -c=c]
  diff_stream.py client [-p=p -r=p -t=t -n=f -a=a -f=f]

Options:
  -p=p --pubsub=p    Port # for pub sub communication [default: 5556]
  -r=r --reqres=p    Port # for req res communication [default: 5557]
  -t=t --topic=t     Pubsub topic [default: _a_topic_]
  -n=f --fname=f     Filename to save stats pickle to [default: ]
  -s=s --sleep=s     Sleep between published messages (in sec) [default: 1]
  -u=a --auctions=a  Number of auction items being run [default: 1]
  -c=c --count=c     Number of messages generated [default: 100]
  -a=a --addr=a      Address where the server is running [default: localhost]
  -f=f --fuzz=f      Failure rate [default: 0.05]
  -h   --help        Show this message
"""

from docopt import docopt
from app import client
from app import server


if __name__ == '__main__':
    args = docopt(__doc__)
    print(args)

    addr = args['--addr']
    topic = args['--topic']
    pubsub = int(args['--pubsub'])
    reqres = int(args['--reqres'])
    fname = args['--fname'] or None

    if args['client']:
        client.start(addr, pubsub, reqres, topic,
                     fuzz=float(args['--fuzz']),
                     fname=fname)

    elif args['server']:
        server.start(pubsub, reqres, topic,
                     sleep=float(args['--sleep']),
                     auctions=int(args['--auctions']),
                     count=int(args['--count']),
                     fname=fname)
