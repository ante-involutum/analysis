from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware

import prometheus_client


from src.metrics import registry, demo
from src.helper import KFConsumer
from src.env import *

app = FastAPI(name="analysis")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/analysis/metrics', response_class=PlainTextResponse)
async def metrics():
    c = KFConsumer(
        KAFKA_SERVICE_HOSTS,
        'atop'
    )
    c.subscribe(pattern='^demo-*')
    result = c.poll()
    for i in result:
        task_type = i['value']['task_type']
        task_name = i['value']['task_name']
        demo.labels(task_type, task_name, 'data').set(i['value']['data'])
    c.close()
    return prometheus_client.generate_latest(registry)


@app.get('/analysis/raw/{topic}')
async def kafak_msg(topic):
    c = KFConsumer(
        KAFKA_SERVICE_HOSTS,
        'atop'
    )
    c.subscribe(topics=(topic))
    result = c.poll()
    c.close()
    return result
