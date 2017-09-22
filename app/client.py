"""
Stream client supporing subscriptions and retransmission requests.

Leverages zeromq for IPC.
"""

import asyncio as aio
import zmq
import zmq.asyncio
import uuid
import random
import signal
import pickle
from cache import consts
from cache import cache
from cache import patch
from stream import protocol
from stream import stats


def initialize_zmq(server_addr, pubsub_port, reqres_port):
    """
    Setup zmq and required ports.
    """
    zmq.asyncio.install()
    ctx = zmq.asyncio.Context()
    sock_sub = ctx.socket(zmq.SUB)
    sock_sub.connect("tcp://{}:{}".format(server_addr, pubsub_port))
    sock_req = ctx.socket(zmq.REQ)
    sock_req.connect("tcp://{}:{}".format(server_addr, reqres_port))
    return ctx, sock_sub, sock_req


def subscribe(sock, topicfilter):
    """
    Subscribe to the publisher for the given topics.
    """
    for topic in topicfilter:
        print('Subscribing to topic: {}'.format(topic))
        sock.setsockopt(zmq.SUBSCRIBE, topic.encode())


async def request_retrans(sock, my_unique_id, key):
    """
    Send request to server to retransmit the specified key.
    """
    request = protocol.ReqResMsg.retran(my_unique_id, key)
    print('Requesting: {}'.format(request))
    await sock.send_multipart(request.to_network())
    buf = await sock.recv_multipart()
    response = protocol.ReqResMsg.from_network(buf)
    print('Received: {}'.format(response))


async def process_msg(msg, dc):
    """
    Process a message received on the subscription interface.
    """
    msg = patch.DataMsg.from_json(msg)
    # print('Received msg: {}'.format(msg))

    try:
        cmd, key, data = dc.update(msg)
    except Exception as e:
        print('ValueError: {}'.format(e))
        print('Requesting a retransmission ...')
        return False, msg.key, None

    # print('Hydrated: {}'.format(data))
    return True, msg.key, cmd


def cleanup():
    """
    Clean up event loop to prepare for exit.
    """
    print('Canceling outstanding tasks')
    for task in aio.Task.all_tasks():
        task.cancel()


async def run(sock_sub, sock_req, my_unique_id, fuzz, stat):
    """
    Run the client.
    """
    dc = cache.DiffCache.consumer()

    while True:
        buf = await sock_sub.recv_multipart()
        msg = protocol.PubSubMsg.from_network(buf)
        # print('Received {}'.format(msg))

        success, key, cmd = await process_msg(msg.payload, dc)
        # Insert artificial dataloss (using the fuzz factor)
        stat.transmitted(len(buf[2]), dc.get(key, None), cmd, key)

        if not success or random.random() < fuzz:
            await request_retrans(sock_req, my_unique_id, key)


def start(host_addr, pubsub_port, reqres_port, topic_string, **kwargs):
    print('Connecting to server on {}'.format(host_addr))

    fuzz = kwargs.get('fuzz', 0.0)
    fname = kwargs.get('fname', None)

    ctx, sock_sub, sock_req = initialize_zmq(
        host_addr, pubsub_port, reqres_port)

    my_unique_id = uuid.uuid4().hex
    subscribe(sock_sub, (topic_string, my_unique_id))

    loop = aio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, cleanup)

    print('Ctrl+C to exit')

    stat = stats.UtilizationStats(track_bytes=True,
                                  track_keys=True,
                                  track_messages=True,
                                  report_interval=100)

    try:
        aio.get_event_loop().run_until_complete(
            run(sock_sub, sock_req, my_unique_id, fuzz, stat))
    except aio.CancelledError:
        print('Closing zmq connection')
        sock_sub.close()
        sock_req.close()
        ctx.term()
    finally:
        loop.close()

    if fname:
        with open(fname, 'wb') as p_file:
            pickle.dump(stat.stats_lst, p_file)
            print('Stats written to {}'.format(fname))
