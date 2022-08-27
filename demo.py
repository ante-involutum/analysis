import json
import asyncio
import traceback
from threading import Thread

from loguru import logger
from aiokafka import AIOKafkaConsumer
import redis


bootstrap_servers = 'middleware-kafka.tink:9092'


r = redis.Redis(
    host='127.0.0.1',
    port=6379,
    decode_responses=True,
    password='changeme'
)

tasks = {}


async def consume(topic):
    while True:
        logger.info(f'consume: {topic}')
        await asyncio.sleep(1)


async def monitor():
    ps = r.pubsub()
    ps.subscribe('add', 'del')
    for msg in ps.listen():
        if msg['type'] == 'message':
            if msg['channel'] == 'add':
                data = msg['data']
                f = asyncio.run_coroutine_threadsafe(
                    consume(data),
                    thread_loop
                )
                tasks[data] = f
                logger.info(f'add tasks: {data}')

            if msg['channel'] == 'del':
                data = msg['data']
                f = tasks[data]
                f.cancel()
                tasks.pop(data)
                logger.info(f'del tasks: {data}')

        logger.info(f'all tasks: {tasks}')


def start_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


thread_loop = asyncio.new_event_loop()
run_loop_thread = Thread(target=start_loop, args=(thread_loop,))
run_loop_thread.start()


advocate_loop = asyncio.get_event_loop()
advocate_loop.run_until_complete(monitor())
