from typing import List
from pprint import pprint
from loguru import logger
from requests import Session
from fastapi import WebSocket
from elasticsearch import Elasticsearch
from prometheus_client import CollectorRegistry, Gauge, generate_latest


from src.env import ELASTICSEARCH_SERVICE_HOSTS
from src.env import KS_SERVICE_HOSTS
from src.env import KS_SERVICE_USER
from src.env import KS_SERVICE_PWD
from src.env import NAMESPACE


class EsHelper():

    def __init__(self) -> None:
        self.host = ELASTICSEARCH_SERVICE_HOSTS
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
        hits = result['hits']['hits']
        _sources = list(map(lambda x: x['_source'], hits))
        sort = list(map(lambda x: x['sort'], hits))

        for i in _sources:
            messages.append(i['message'])

        total = len(messages)
        resp['total'] = total
        if total == 0:
            resp['offset'] = None
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


class KsHelper():

    def __init__(self) -> None:
        self.svc = KS_SERVICE_HOSTS
        self.user = KS_SERVICE_USER
        self.pwd = KS_SERVICE_PWD
        self.is_auth = None
        self.session = Session()

    def auth(self):
        payload = {
            'grant_type': 'password',
            'username': self.user,
            'password': self.pwd,
            'client_id': 'kubesphere',
            'client_secret': 'kubesphere',
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        resp = self.session.post(
            f'{self.svc}/oauth/token',
            data=payload,
            headers=headers
        )
        resp = resp.json()
        access_token = resp['access_token']
        self.session.headers['Authorization'] = f'Bearer {access_token}'
        self.is_auth = True

    def get_logs(self, pod, container, from_, size):
        payload = {
            'operation': 'query',
            'log_query': '',
            'pods': pod,
            'containers': container,
            'from': from_,
            'size': size,
            'interval': '1d',
            'sort': 'asc',
            # 'sort': 'desc',
            'namespaces': NAMESPACE
        }
        headers = {
            'Content-Type': 'application/json'
        }
        resp = self.session.get(
            f'{self.svc}/kapis/tenant.kubesphere.io/v1alpha2/logs',
            params=payload,
            headers=headers
        )
        resp = resp.json()
        return resp

    def fmt(self, resp):
        result = {}
        messages = []

        records = resp.get('query', {}).get('records', None)
        if records is None:
            pass
        else:
            for x in records:
                messages.append(x['log'])

        result['messages'] = messages
        result['total'] = len(messages)
        return result
