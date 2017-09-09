"""
Stream client supporing subscriptions and retransmission requests.

Leverages zeromq for IPC.
"""

import asyncio as aio
import zmq
import zmq.asyncio
import uuid
import constants as const
from diffstream import cache
from diffstream import protocol


def initialize_zmq():
    """Setup zmq and required ports"""
    zmq.asyncio.install()
    ctx = zmq.asyncio.Context()
    sock_sub = ctx.socket(zmq.SUB)
    sock_sub.connect("tcp://{}:{}".format(
        const.PUB_SUB_HOST, const.PUB_SUB_PORT))
    sock_req = ctx.socket(zmq.REQ)
    sock_req.connect("tcp://{}:{}".format(
        const.REQ_RES_HOST, const.REQ_RES_PORT))
    return ctx, sock_sub, sock_req


def subscribe(sock, topicfilter):
    """Subscribe to the publisher for the given topic"""
    print('Subscribing using filter: {}'.format(topicfilter))
    for topic in topicfilter:
        sock.setsockopt(zmq.SUBSCRIBE, topic)


async def request_retrans(sock, my_unique_id, key):
    """Send request to server to retransmit the specified key"""
    request = protocol.ReqResCmd.retran(my_unique_id, key)
    print('Requesting: {}'.format(request))
    await sock.send_multipart(request.to_network())
    buf = await sock.recv_multipart()
    response = protocol.ReqResCmd.from_network(buf)
    print('Received: {}'.format(response))


async def process_msg(msg, dc):
    """Process a message received on the subscription interface"""
    msg = cache.DataMsg.from_json(msg)
    # print('Received msg: {}'.format(msg))

    try:
        cmd, key, data = dc.update(msg)
    except Exception as e:
        print('ValueError: {}'.format(e))
        print('Requesting a retransmission ....')
        return False, msg.key

    print('Hydrated: {}'.format(data))
    return True, msg.key


async def cleanup():
    print('Canceling outstanding tasks')
    for task in aio.Task.all_tasks():
        task.cancel()


async def run(sock_sub, sock_req, my_unique_id):
    dc = cache.DiffCache.consumer()

    while True:
        buf = await sock_sub.recv_multipart()
        msg = protocol.PubSubBuf.from_network(buf)
        # print('Received {}'.format(msg))

        success, key = await process_msg(msg.payload, dc)
        if not success:
            await request_retrans(sock_req, my_unique_id, key)


def main():
    print('Initializing zmq connection')
    ctx, sock_sub, sock_req = initialize_zmq()

    my_unique_id = uuid.uuid4().hex
    subscribe(sock_sub, (const.TOPIC_STRING, my_unique_id.encode()))

    print('Ctrl+C to exit')

    try:
        aio.get_event_loop().run_until_complete(
            run(sock_sub, sock_req, my_unique_id))
    except KeyboardInterrupt:
        aio.get_event_loop().run_until_complete(cleanup())

    print('Closing zmq connection')
    sock_sub.close()
    sock_req.close()
    ctx.term()
    aio.get_event_loop().close()


if __name__ == "__main__":
    main()
