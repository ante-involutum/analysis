from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware

from src.env import *
import prometheus_client
from kafka import KafkaConsumer
from src.metrics import registry, jmeter
from src.helper import msg_to_dict


app = FastAPI(name="analysis")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


origin_consumer = KafkaConsumer(
    'jmx',
    group_id='origin',
    bootstrap_servers=['middleware-kafka.tink:9092'],
    auto_offset_reset='earliest'
)

metrics_consumer = KafkaConsumer(
    'jmx',
    group_id='metrics',
    bootstrap_servers=['middleware-kafka.tink:9092'],
    auto_offset_reset='earliest',
)


@app.get('/metrics', response_class=PlainTextResponse)
def get_data():
    msg = next(metrics_consumer)
    value = eval(msg.value.decode("UTF-8"))['message']

    for k, v in msg_to_dict(value).items():
        jmeter.labels('jmeter', msg.topic, k).set(v)

    return prometheus_client.generate_latest(registry)


@app.get('/analysis/kafak')
def get_kafak_data():
    msg = next(origin_consumer)
    result = eval(msg.value.decode("UTF-8"))
    return result
