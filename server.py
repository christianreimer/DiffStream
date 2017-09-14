"""
Stream server supporting publications and retransmission requests.

Leverages zmq for IPC
"""

import asyncio as aio
import zmq
import zmq.asyncio
import random
import data
from cache import cache
from cache import consts
from stream import protocol
from stream import PUB_SUB_PORT, PUB_SUB_HOST, REQ_RES_PORT, REQ_RES_HOST, TOPIC_STRING


def initialize_zmq():
    """Setup zmq and required ports"""
    zmq.asyncio.install()
    ctx = zmq.asyncio.Context()
    sock_pub = ctx.socket(zmq.PUB)
    sock_pub.bind("tcp://*:{}".format(PUB_SUB_PORT))
    sock_rep = ctx.socket(zmq.REP)
    sock_rep.bind("tcp://*:{}".format(REQ_RES_PORT))
    return ctx, sock_pub, sock_rep


async def publish(sock_pub, topic, corr_id, msg):
    """Publish msg using the given topic string"""
    pub_msg = protocol.PubSubMsg(topic, corr_id, msg)
    await sock_pub.send_multipart(pub_msg.to_network())


async def process_retran_request(sock_pub, sock_rep, dc):
    """Listen for retransmission requests on the request socket, and initiate
    republish using the requesters topic string"""
    while True:
        buf = await sock_rep.recv_multipart()
        request = protocol.ReqResMsg.from_network(buf)
        print('Received: {}'.format(request))

        if request.cmd not in (consts._cmd_ret_, ):
            response = protocol.ReqResMsg.nack(request.corr_id)
            print('Responding: {}'.format(response))
            await sock_rep.send_multipart(response.to_network())

        else:
            response = protocol.ReqResMsg.ack(request.corr_id)
            await sock_rep.send_multipart(response.to_network())
            print('Responding: {}'.format(response))

            msg = dc.retran(request.key)
            await publish(sock_pub, request.unique_id, request.corr_id, msg)


async def cleanup():
    """Clean up event loop to prepare for exit"""
    print('Canceling outstanding tasks')
    for task in aio.Task.all_tasks():
        task.cancel()


async def run(sock_pub, sock_rep, dc):
    """Run the server"""
    auction_lst = []
    for _ in range(4):
        auction_lst.append(data.auction_generator())

    while True:
        auction = random.choice(auction_lst)
        auction_update = auction.__next__()
        print('Auction Update: {}'.format(auction_update))
        msg = dc.update(auction_update)
        await publish(sock_pub, TOPIC_STRING, '', msg)
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
