import re
import json
from typing import List

from kafka import KafkaConsumer
from fastapi import HTTPException, WebSocket


def time_to_float(time_str):
    h, m, s = time_str.strip().split(":")
    return float(h) * 3600 + float(m) * 60 + float(s)


def msg_to_dict(msg):
    _ = msg.replace(" ", "")

    if 'summary' in _ and 'Avg' in _:
        values = re.compile(
            r"summary.(\d*)in(.*)=(.*)Avg:(\d*)Min:(\d*)Max:(\d*)Err:(\d*)(.*)"
        ).findall(_)[0]

        result = {
            'summary': float(values[0]),
            'duration_time': time_to_float(values[1]),
            'rps': float(values[2].replace("/s", "")),
            'avg': float(values[3]),
            'min': float(values[4]),
            'max': float(values[5]),
            'erro': float(values[6]),
        }
    else:
        result = {
            'summary': 0,
            'duration_time': 0,
            'rps': 0,
            'avg': 0,
            'min': 0,
            'max': 0,
            'erro': 0,
        }
    return result


def query(es, task_tag, task_name, _from, size):
    resp = {}
    body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {
                            "task_name": task_name
                        }
                    },
                    {
                        "term": {
                            "task_tag": task_tag
                        }
                    }
                ],
                "must_not": [

                ],
                "should": [

                ]
            }
        },
        "from": _from,
        "size": size,
        "sort": [],
        "aggs": {

        }
    }
    try:
        result = es.search(index="atop", body=body)
        total = result['hits']['total']['value']
        hits = result['hits']['hits']
        _sources = list(map(lambda x: x['_source'], hits))
        resp['total'] = total
        resp['_sources'] = _sources
        return resp
    except Exception as e:
        raise HTTPException(status_code=e.meta.status, detail=e.message)


class KFConsumer():

    def __init__(self, hosts, group_id):

        self.group_id = group_id
        self.servers = hosts
        self.auto_offset_reset = 'earliest'
        self.value_deserializer = lambda m: json.loads(m.decode('UTF-8'))
        self.c = KafkaConsumer(
            group_id=self.group_id,
            bootstrap_servers=self.servers,
            auto_offset_reset=self.auto_offset_reset,
            value_deserializer=self.value_deserializer,
            auto_commit_interval_ms=1000
        )

    def subscribe(self, topics=(), pattern=None):
        self.c.subscribe(
            topics=topics,
            pattern=pattern
        )

    def poll(self, timeout=5000, max_records=1):
        msgs = self.c.poll(timeout, max_records)
        result = []
        for msg in msgs.values():
            for _ in msg:
                msg_dict = dict()
                msg_dict['offset'] = _.offset
                msg_dict['topic'] = _.topic
                msg_dict['partition'] = _.partition
                msg_dict['timestamp'] = _.timestamp
                msg_dict['value'] = _.value
                msg_dict['timestamp_type'] = _.timestamp_type
                msg_dict['headers'] = _.headers
                msg_dict['checksum'] = _.checksum
                msg_dict['serialized_key_size'] = _.serialized_key_size
                msg_dict['serialized_value_size'] = _.serialized_value_size
                msg_dict['serialized_header_size'] = _.serialized_header_size
                result.append(msg_dict)
        return result

    def close(self):
        self.c.close()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)
