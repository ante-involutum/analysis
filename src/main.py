import json
from typing import List
from loguru import logger
from elasticsearch import Elasticsearch
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, WebSocket, WebSocketDisconnect


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


manager = ConnectionManager()


@app.get('/analysis/raw/{task_name}')
async def kafak_msg(task_name, _from: int = 0, size: int = 10):
    query = {
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
                            "task_tag": "raw"
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
        "sort": [
            "timestamp"
        ],
        "aggs": {

        }
    }
    result = es.search(index="atop", body=query)
    return result


@app.websocket("/analysis/ws/{task_name}")
async def websocket_endpoint(task_name, websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            _from = data['_from']
            size = data['size']
            query = {
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
                                    "task_tag": "raw"
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
                "sort": [
                    "timestamp"
                ],
                "aggs": {

                }
            }
            result = es.search(index="atop", body=query)
            logger.info(result)
            await manager.send_personal_message(json.dumps(result.raw), websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
