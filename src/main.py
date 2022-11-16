import json
from pprint import pprint
from elasticsearch import Elasticsearch
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from src.helper import query, ConnectionManager
from src.env import ELASTICSEARCH_SERVICE_HOSTS


app = FastAPI(name="analysis")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

es = Elasticsearch(hosts=ELASTICSEARCH_SERVICE_HOSTS)

manager = ConnectionManager()


@app.get('/analysis/raw')
async def get_raw(task_tag: str, task_name: str, _from: int = 0, size: int = 10):
    result = query(es, task_tag, task_name, _from, size)
    messages = []
    for i in result['_sources']:
        messages.append(i['message'])
    result['messages'] = messages
    pprint(result)
    return result


@app.websocket("/analysis/ws/raw")
async def websocket_msg(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            _from = data['_from']
            size = data['size']
            task_tag = data['task_tag']
            task_name = data['task_name']
            result = query(es, task_tag, task_name, _from, size)
            messages = []
            for i in result['_sources']:
                messages.append(i['message'])
            result['messages'] = messages

            # just for qingtest front
            if data.get('task_id', None) != None:
                result['task_id'] = data['task_id']

            pprint(result)
            await manager.send_personal_message(json.dumps(result), websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
