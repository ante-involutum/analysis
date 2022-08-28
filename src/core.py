import json
import redis
import asyncio
import traceback
from threading import Thread

from loguru import logger
from aiokafka import AIOKafkaConsumer


tasks = {}
bootstrap_servers = 'middleware-kafka.tink:9092'


r = redis.Redis(
    host='middleware-redis-headless.tink',
    port=6379,
    decode_responses=True,
    password='changeme'
)


async def consume(topic):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        value_deserializer=lambda m: json.loads(m.decode('UTF-8')),
        auto_offset_reset='earliest',
        group_id=topic
    )
    try:
        await consumer.start()
        logger.info(f'start {topic}')
        async for msg in consumer:
            logger.info(msg)
    except Exception as e:
        logger.debug(e)
        logger.error(traceback.format_exc())
    finally:
        await consumer.stop()
        logger.info(f'stop {topic}')


async def monitor():
    for _ in r.lrange('tasks', 0, -1):
        f = asyncio.run_coroutine_threadsafe(
            consume(_),
            thread_loop
        )
        tasks[_] = f
        logger.info(f'restart tasks: {_}')

    ps = r.pubsub()
    ps.subscribe('add', 'del')
    for msg in ps.listen():
        if msg['type'] == 'message':
            data = msg['data']
            if data in tasks.keys():
                pass

            if msg['channel'] == 'add':
                f = asyncio.run_coroutine_threadsafe(
                    consume(data),
                    thread_loop
                )
                tasks[data] = f
                logger.info(f'add tasks: {data}')

            if msg['channel'] == 'del':
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
