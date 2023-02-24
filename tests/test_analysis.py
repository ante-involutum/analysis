import json
import pytest
import websocket
from loguru import logger
from pprint import pprint


@pytest.mark.usefixtures('init')
class TestAnalysis():

    payload = {
        'index': 'logs',
        'key_words': {
            'pod.name': 'lunz233',
            'container.name': 'aomaker',
            'labels.uid': '741b0b32-1d9e-4dac-86ea-8bc32493f67c'
        },
        "from_": 0,
        "size": 20,
        "offset": [1676991917964, 'CCSCdIYB_m0N6VTGB8OO']
    }
    header = {
        "Authorization": "admin"
    }

    def test_msg(self):
        resp = self.bs.post(
            '/analysis/raw',
            headers=self.header,
            json=self.payload
        )
        pprint(resp.json())
        assert resp.status_code == 200

    def test_ws(self):
        ws = websocket.WebSocket()
        ws.connect(
            self.ws_url,
            header=self.header
        )
        ws.send(json.dumps(self.payload))
        resp = ws.recv()
        pprint(json.loads(resp))
        assert ws.status == 101
