from random import random
import time
import redis
import json
import asyncio
import traceback
import threading

from loguru import logger


redis_client = redis.Redis(
    host='127.0.0.1',
    port=6379,
    decode_responses=True,
    password='changeme'
)


# r.set('test', 1)
# r.publish("add", 'demo-1')
# r.publish("add", 'demo-0')
# r.publish("del", 'demo-0')

# redis_client.lpush("tasks", 'demo-1')


# print(redis_client.lrange('tasks', 0, -1))


# redis_client.lrem('tasks', 0, 'demo-1')


a = redis_client.lrange('tasks', 0, -1)
print(a)
