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
            'pod.name': 'lunz',
            'container.name': 'aomaker',
            'labels.uid': '5a9a414b-84fa-477c-8701-557a1d40a38e'
        },
        "from_": 0,
        "size": 20
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
        assert resp.status_code == 200

    def test_ws(self):
        ws = websocket.WebSocket()
        ws.connect(
            self.ws_url,
            header=self.header
        )
        ws.send(json.dumps(self.payload))
        resp = ws.recv()
        logger.info(resp)
        pprint(json.loads(resp))
        assert ws.status == 101
