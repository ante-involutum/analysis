import json
import logging
import traceback

from fastapi import FastAPI
from fastapi import WebSocket
from fastapi import HTTPException
from fastapi import WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from elasticsearch_dsl import Search, Q
from elasticsearch import ApiError, Elasticsearch


from src.model import Query
from src.utils import ConnectionManager
from src.env import ELASTICSEARCH_SERVICE_HOSTS

app = FastAPI(name="analysis")
logger = logging.getLogger("uvicorn.error")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

manager = ConnectionManager()
es = Elasticsearch(ELASTICSEARCH_SERVICE_HOSTS)


@app.post("/logs")
async def get_logs_with_http(q: Query):
    try:
        logger.debug(q)
        s = Search(using=es, index="filebeat-*").extra(size=q.size)

        if q.offset != None:
            s = s.extra(search_after=q.offset)
        else:
            if q.from_ != None:
                s = s.extra(from_=q.from_)

        s = s.query(
            "bool",
            must=[Q("term", **{k: v}) for k, v in q.key_words.items()],
        )

        s = s.sort({"@timestamp": {"order": "asc"}})
        response = s.execute()
        total = response.hits.total.value

        resp = {}
        hits = [hit.to_dict() for hit in response]
        messages = [hit.get("message") for hit in hits]
        resp["total"] = total
        resp["messages"] = messages

        if len(messages) == 0:
            resp["offset"] = q.offset
        else:
            offset = response.hits.hits[-1].sort.to_list()
            resp["offset"] = offset

        logger.debug(resp)
        return resp

    except ApiError as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=e.status_code, detail=e.message)

    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="内部错误")


@app.websocket("/logs/ws")
async def get_logs_with_ws(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)

            size = data.get("size")
            from_ = data.get("from_")
            offset = data.get("offset")
            key_words = data.get("key_words")

            q = Query(
                index="logs",
                from_=from_,
                offset=offset,
                size=size,
                key_words=key_words,
            )
            
            logger.debug(q)
            s = Search(using=es, index="filebeat-*").extra(size=q.size)

            if offset != None:
                s = s.extra(search_after=q.offset)
            else:
                if from_ != None:
                    s = s.extra(from_=q.from_)

            s = s.query(
                "bool",
                must=[Q("term", **{k: v}) for k, v in q.key_words.items()],
            )

            s = s.sort({"@timestamp": {"order": "asc"}})
            response = s.execute()
            total = response.hits.total.value

            result = {}
            hits = [hit.to_dict() for hit in response]
            messages = [hit.get("message") for hit in hits]
            result["total"] = total
            result["messages"] = messages

            if len(messages) == 0:
                result["offset"] = offset
            else:
                offset = response.hits.hits[-1].sort.to_list()
                result["offset"] = offset

            if data.get("task_id") != None:
                result["task_id"] = data["task_id"]

            logger.debug(result)
            await manager.send_personal_message(result, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)

    except ApiError as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=e.status_code, detail=e.message)

    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="内部错误")
