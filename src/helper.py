from typing import List
from loguru import logger
from fastapi import WebSocket
from elasticsearch import Elasticsearch
from prometheus_client import CollectorRegistry, Gauge, generate_latest


class EsHelper():

    def __init__(self, host) -> None:
        self.host = host
        self.client = Elasticsearch(self.host)

    def index(self, index):
        result = self.client.indices.create(index=index, ignore=400)
        return result

    def insert(self, index, id, data):
        result = self.client.index(index=index, id=id, document=data)
        return result

    def get(self, index, id):
        result = self.client.get(index=index, id=id)
        return result

    def delete(self, index, id):
        result = self.client.delete(index=index, id=id)
        return result

    def update(self, index, id, doc):
        result = self.client.update(index=index, id=id, doc=doc)
        return result

    def search(self, index, key_words, _from, size, search_after, type='must', mod='term'):
        q = {
            'query': {
                'bool': {}
            },
            "sort": [{
                "@timestamp": "asc",
                "_id": "asc",
            }],
            "aggs": {}
        }
        q['from'] = _from
        q['size'] = size
        q['query']['bool'][type] = []
        for k, v in key_words.items():
            q['query']['bool'][type].append(
                {
                    mod: {
                        f'{k}.keyword': v}
                }
            )

        result = self.client.search(
            index=index,
            body=q,
            search_after=search_after
        )
        resp = {}
        messages = []
        # total = result['hits']['total']['value']
        hits = result['hits']['hits']
        _sources = list(map(lambda x: x['_source'], hits))
        sort = list(map(lambda x: x['sort'], hits))

        for i in _sources:
            messages.append(i['message'])

        # resp['total'] = total
        # resp['_sources'] = _sources
        total = len(messages)
        resp['total'] = total
        if total == 0:
            resp['offset'] = []
        else:
            resp['offset'] = sort[-1]
        resp['messages'] = messages
        return resp


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


class PrometheusHekper():

    def __init__(self) -> None:

        self.registry = CollectorRegistry()
        self.tink_task_status = Gauge(
            'tink_task_status',
            'pod status by tink created',
            ['name', 'type', 'namespace'],
            registry=self.registry
        )

    def generate_latest(self):
        return generate_latest(self.registry)
