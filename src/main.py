import json
import traceback
from loguru import logger
from fastapi import FastAPI
from fastapi import WebSocket
from fastapi import HTTPException
from fastapi import WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from src.model import Query
from src.helper import ConnectionManager, EsHelper, KsHelper

app = FastAPI(name="analysis")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

manager = ConnectionManager()
es = EsHelper()
ks = KsHelper()


@app.on_event("startup")
async def startup_event():
    try:
        ks.auth()
    except Exception as e:
        logger.debug(e)
        logger.error(traceback.format_exc())


@app.post('/analysis/raw')
async def get_logs_from_es(q: Query):
    try:
        logger.info(q)
        result = es.search(q.index, q.key_words, q.from_, q.size, q.offset)
        logger.info(result)
        return result
    except Exception as e:
        logger.debug(e)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail='内部错误')


@app.websocket("/analysis/ws/raw")
async def websocket_logs_from_es(websocket: WebSocket):
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
    except Exception as e:
        logger.debug(e)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail='内部错误')


@app.post('/analysis/raw/v1.1')
async def get_logs_from_ks(q: Query):
    try:
        resp = ks.get_logs(
            q.key_words['pod.name'],
            q.key_words['container.name'],
            q.from_,
            q.size
        )
        result = ks.fmt(resp)
        logger.info(result)
        return result
    except Exception as e:
        logger.debug(e)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail='内部错误')


@app.websocket("/analysis/ws/raw/v1.1")
async def websocket_logs_from_ks(websocket: WebSocket):
    try:
        await manager.connect(websocket)
        offset = 0
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            logger.info(data)

            _from = data.get('from_', 0)
            size = data['size']
            key_words = data['key_words']

            _from = _from + offset*size

            resp = ks.get_logs(
                key_words['pod.name'],
                key_words['container.name'],
                _from,
                size
            )

            result = ks.fmt(resp)

            # just for qingtest front
            if data.get('task_id', None) != None:
                result['task_id'] = data['task_id']

            resp = json.dumps(result, ensure_ascii=False)
            logger.info(result)
            offset = offset + 1
            await manager.send_personal_message(resp, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.debug(e)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail='内部错误')
