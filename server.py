"""
Stream server supporing publications and retransmission requests.

Leverages zmq for IPC
"""

import asyncio as aio
import zmq
import zmq.asyncio
import random
import constants as const
import data
from diffstream import cache
from diffstream import consts
import uuid


def initialize_zmq():
    """Setup zmq and required ports"""
    zmq.asyncio.install()
    ctx = zmq.asyncio.Context()
    sock_pub = ctx.socket(zmq.PUB)
    sock_pub.bind("tcp://*:{}".format(const.PUB_SUB_PORT))
    sock_rep = ctx.socket(zmq.REP)
    sock_rep.bind("tcp://*:{}".format(const.REQ_RES_PORT))
    return ctx, sock_pub, sock_rep


async def publish(sock_pub, topic, corr_id, msg):
    """Publish msg using the given topic string"""
    if not isinstance(topic, bytes):
        topic = topic.encode()

    if not isinstance(corr_id, bytes):
        corr_id = corr_id.encode()

    if not isinstance(msg, bytes):
        msg = msg.encode()

    await sock_pub.send_multipart((topic, corr_id, msg))


async def process_retran_request(sock_pub, sock_rep, dc):
    """Listen for retransmission requests on the request socket, and initiate
    republish using the requesters topic string"""
    while True:
        cmd, unique_id, key = await sock_rep.recv_multipart()
        print('Received request {} from 0x{} regarding 0x{}'.format(
            consts.cmd_name[cmd.decode()],
            unique_id.decode()[:6],
            key.decode()[:6]))

        cmd = cmd.decode()

        if cmd not in (consts._cmd_ret_, ):
            print('Sending back NACK')
            await sock_rep.send_multipart((b'NACK', b''))

        else:
            corr_id = uuid.uuid4().hex
            await sock_rep.send_multipart((b'ACK', corr_id.encode()))

            print('Sending back ACK')
            msg = dc.retran(key)
            await publish(sock_pub, unique_id, corr_id, msg)


async def cleanup():
    """Clean up event loop to prepare for exit"""
    print('Canceling outstanding tasks')
    for task in aio.Task.all_tasks():
        task.cancel()


async def run(sock_pub, sock_rep, dc):
    """Run the server"""
    auction_lst = []
    for _ in range(3):
        auction_lst.append(data.auction_generator())

    while True:
        auction = random.choice(auction_lst)
        auction_update = auction.__next__()
        # print('Auction Update: {}'.format(auction_update))
        msg = dc.update(auction_update)
        await publish(sock_pub, const.TOPIC_STRING, '', msg)
        await aio.sleep(1)


def main():
    print('Initializing zmq connection')
    ctx, sock_pub, sock_rep = initialize_zmq()

    print('Ctrl+C to exit')

    loop = aio.get_event_loop()
    dc = cache.DiffCache.producer(key_name='key')

    try:
        loop.create_task(process_retran_request(sock_pub, sock_rep, dc))
        loop.run_until_complete(run(sock_pub, sock_rep, dc))
    except KeyboardInterrupt:
        loop.run_until_complete(cleanup())

    print('Closing zmq connection')
    sock_pub.close()
    sock_rep.close()
    ctx.term()
    loop.close()


if __name__ == "__main__":
    main()
