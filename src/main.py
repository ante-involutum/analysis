from typing import List
from loguru import logger
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from src.helper import KFConsumer
from src.env import *

app = FastAPI(name="analysis")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


@app.on_event("startup")
async def startup_event():
    pass


@app.on_event("shutdown")
def shutdown_event():
    pass


@app.get('/analysis/raw/{topic}')
async def kafak_msg(topic):
    c = KFConsumer(
        KAFKA_SERVICE_HOSTS,
        'atop'
    )
    c.subscribe(topics=(topic))
    result = c.poll()
    c.close()
    return result


@app.websocket("/analysis/ws/{topic}")
async def websocket_endpoint(topic, websocket: WebSocket):
    await manager.connect(websocket)
    try:
        c = KFConsumer(
            KAFKA_SERVICE_HOSTS,
            'atop'
        )
        c.subscribe(topics=(topic))
        while True:
            data = await websocket.receive_text()
            result = c.poll(timeout=2000, max_records=int(data))
            logger.info(result)
            await manager.send_personal_message(f"You wrote: {result}", websocket)
    except WebSocketDisconnect:
        c.close()
        manager.disconnect(websocket)


@app.get("/analysis/")
async def get():
    return HTMLResponse("""
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://127.0.0.1:8005/analysis/ws/demo-1");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
""")
