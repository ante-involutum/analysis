import json
from pprint import pprint
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from src.model import Query

from src.helper import ConnectionManager, EsHelper
from src.env import ELASTICSEARCH_SERVICE_HOSTS

app = FastAPI(name="analysis")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

manager = ConnectionManager()
es = EsHelper(ELASTICSEARCH_SERVICE_HOSTS)


@app.post('/analysis/raw')
async def get_raw(q: Query):

    result = es.search_logs(q.index, q.key_words, q.from_, q.size)
    pprint(result)

    return result


@app.websocket("/analysis/ws/raw")
async def websocket_msg(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()

            data = json.loads(data)
            _from = data['from_']
            size = data['size']
            index = data['index']
            key_words = data['key_words']

            result = es.search_logs(index, key_words, _from, size)

            # just for qingtest front
            if data.get('task_id', None) != None:
                result['task_id'] = data['task_id']

            pprint(result)
            await manager.send_personal_message(json.dumps(result), websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
