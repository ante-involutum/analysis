import json
from pprint import pprint
from loguru import logger
from elasticsearch import Elasticsearch
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from src.helper import query, ConnectionManager


app = FastAPI(name="analysis")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

es = Elasticsearch(
    hosts='http://middleware-elasticsearch-master-headless:9200'
    # hosts='http://127.0.0.1:9200'
)

manager = ConnectionManager()


@app.get('/analysis/raw/{task_name}')
async def msg(task_name, _from: int = 0, size: int = 10):
    result = query(es, task_name, _from, size)
    pprint(result)
    return result


@app.websocket("/analysis/ws/{task_name}")
async def websocket_msg(task_name, websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            _from = data['_from']
            size = data['size']
            result = query(es, task_name, _from, size)
            pprint(result)
            await manager.send_personal_message(json.dumps(result), websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
