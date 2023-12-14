import json
import pytest
import websocket
from pprint import pprint


@pytest.mark.usefixtures('init')
class TestAnalysis():

    payload = {
        'index': 'logs',
        'key_words': {
            'kubernetes.pod.name': '06be8094-265b-49c9-a156-7b8982004272',
            'kubernetes.container.name': 'aomaker',
            # 'kubernetes.container.name': 'sidecar',
        },
        "from_": 0,
        "size": 200,
    }

    def test_get_version(self):
        resp = self.bs.get(
            f'{self.url}/v1.0/version'
        )
        pprint(resp.json())
        assert resp.status_code == 200

    def test_es_log(self):
        resp = self.bs.post(
            f'{self.url}/v1.0/raw',
            json=self.payload
        )
        pprint(resp.json())
        assert resp.status_code == 200

        self.payload['offset'] = resp.json()['offset']
        ws = websocket.WebSocket()
        ws.connect(
            f'{self.ws_url}/v1.0/ws/raw',
        )
        ws.send(json.dumps(self.payload))
        resp = ws.recv()
        pprint(json.loads(resp))
        assert ws.status == 101
