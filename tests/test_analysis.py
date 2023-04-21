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
            'kubernetes.labels.app': 'aomaker-test-1',
        },
        "from_": 0,
        "size": 200,
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

        self.payload['offset'] = resp.json()['offset']
        ws = websocket.WebSocket()
        ws.connect(
            self.ws_url,
            header=self.header
        )
        ws.send(json.dumps(self.payload))
        resp = ws.recv()
        pprint(json.loads(resp))
        assert ws.status == 101
