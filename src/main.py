from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware

import prometheus_client
from elasticsearch import Elasticsearch

from src.utils.metrics import registry, demo
from src.utils.helper import KFConsumer
from src.model.analysis import Job
from src.env import *


app = FastAPI(name="analysis")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

es = Elasticsearch(hosts=f'http://{ELASTICSEARCH_SERVICE_HOSTS}')


@app.get('/metrics', response_class=PlainTextResponse)
def metrics():
    c = KFConsumer(
        KAFKA_SERVICE_HOSTS,
        'atop'
    )
    result = c.subscribe(pattern='^demo-*')
    for i in result:
        task_type = i['value']['task_type']
        task_name = i['value']['task_name']
        demo.labels(task_type, task_name, 'data').set(i['value']['data'])
    c.close()
    return prometheus_client.generate_latest(registry)


@app.get('/analysis/original/{topic}')
async def kafak_msg(topic):
    c = KFConsumer(
        KAFKA_SERVICE_HOSTS,
        'atop'
    )
    result = c.subscribe(topics=(topic))
    c.close()
    return result


@app.post('/analysis/report/')
async def es_msg(job: Job):
    query = {
        "term": {
            'task_name': job.job_name
        }
    }
    resp = es.search(
        index=job.job_type,
        query=query,
        size=job.size,
        from_=job.from_
    )
    return resp['hits']['hits']
