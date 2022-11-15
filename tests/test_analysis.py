import json
import pytest
import websocket
from loguru import logger
from pprint import pprint


@pytest.mark.usefixtures('init')
class TestAnalysis():

    header = {
        "Authorization": "admin"
    }

    def test_msg(self):
        payload = {
            'task_name': 'hpc-api-test2-65-61',
            'task_tag': 'aomaker',
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
            'task_name': 'hpc-api-test2-65-61',
            'task_tag': 'aomaker',
            "_from": 60,
            "size": 2
        }
        ws = websocket.WebSocket()
        ws.connect(
            self.ws_url,
            header=self.header
        )
        ws.send(json.dumps(payload))
        resp = ws.recv()
        logger.info(resp)
        pprint(json.loads(resp))
        assert ws.status == 101
