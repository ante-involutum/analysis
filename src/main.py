import json
from loguru import logger
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
    logger.info(q)
    result = es.search(q.index, q.key_words, q.from_, q.size, q.offset)
    logger.info(result)
    return result


@app.websocket("/analysis/ws/raw")
async def websocket_msg(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            logger.info(data)

            _from = data.get('from_', 0)
            size = data['size']
            index = data['index']
            key_words = data['key_words']
            offset = data.get('offset', None)

            result = es.search(index, key_words, _from, size, offset)

            # just for qingtest front
            if data.get('task_id', None) != None:
                result['task_id'] = data['task_id']

            resp = json.dumps(result, ensure_ascii=False)
            logger.info(resp)
            await manager.send_personal_message(resp, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
