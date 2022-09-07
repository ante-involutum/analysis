import json
import pytest
import websocket
from loguru import logger


@pytest.mark.usefixtures('init')
class TestAnalysis():

    header = {
        "Authorization": "admin"
    }

    def test_msg(self):
        payload = {
            'task_name': '1',
            'task_tag': 'raw',
            "_from": 0,
            "size": 2
        }
        resp = self.bs.get(
            '/analysis/raw',
            headers=self.header,
            params=payload
        )
        assert resp.status_code == 200

    def test_ws(self):
        payload = {
            'task_name': '1',
            'task_tag': 'raw',
            "_from": 0,
            "size": 2
        }
        ws = websocket.WebSocket()
        ws.connect(
            # "ws://tink.test:31695/analysis/ws/1",
            "ws://127.0.0.1:8005/analysis/raw",
            header=self.header
        )
        ws.send(json.dumps(payload))
        resp = ws.recv()
        logger.info(resp)
        assert ws.status == 101
