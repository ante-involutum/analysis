import json
import asyncio
import traceback
from threading import Thread

from loguru import logger
from aiokafka import AIOKafkaConsumer


bootstrap_servers = 'middleware-kafka.tink:9092'


async def consume(topic):
    logger.info(f'start {topic}')
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        value_deserializer=lambda m: json.loads(m.decode('UTF-8')),
        auto_offset_reset='earliest',
        group_id="core"
    )

    await consumer.start()
    try:
        async for msg in consumer:
            logger.info(msg)
    except Exception as e:
        logger.debug(e)
        logger.error(traceback.format_exc())
    finally:
        await consumer.stop()
        logger.info(f'stop {topic}')


async def production_task():
    tasks = {}
    c = AIOKafkaConsumer(
        bootstrap_servers=bootstrap_servers,
        group_id="watch"
    )
    await c.start()
    while True:
        await asyncio.sleep(2)
        try:
            topics = await c.topics()
            logger.info(f'all topics {topics}')

            for topic in topics:
                if topic not in tasks.keys():
                    logger.info(f'add topic {topic} to task')
                    future = asyncio.run_coroutine_threadsafe(
                        consume(topic),
                        thread_loop
                    )
                    tasks[topic] = future

            for k, v in tasks.items():
                if k not in topics:
                    v.cancel()
                    del tasks[k]
                    logger.info(f'cancel {k} task')

            logger.info(f'all tasks: {tasks.keys()}')

        except Exception as e:
            logger.debug(e)
            logger.error(traceback.format_exc())


def start_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


thread_loop = asyncio.new_event_loop()
run_loop_thread = Thread(target=start_loop, args=(thread_loop,))
run_loop_thread.start()


advocate_loop = asyncio.get_event_loop()
advocate_loop.run_until_complete(production_task())
