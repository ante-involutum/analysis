from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware

import prometheus_client

from src.metrics import registry, jmeter
from src.helper import msg_to_dict
from src.kafka import get_origin_data_form_kafka, subscribe_origin_data_form_kafka


app = FastAPI(name="analysis")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/metrics', response_class=PlainTextResponse)
def get_data():

    for i in subscribe_origin_data_form_kafka():

        task_type = i['value']['task_type']
        task_name = i['value']['task_name']

        for k, v in msg_to_dict(i['value']['message']).items():
            jmeter.labels(task_type, task_name, k).set(v)

    return prometheus_client.generate_latest(registry)


@app.get('/analysis/kafak/{topic}')
def get_topic_msg(topic):
    result = get_origin_data_form_kafka(topic)
    return result


@app.get('/analysis/kafak')
def sub_topic_msg():
    result = subscribe_origin_data_form_kafka()
    return result
