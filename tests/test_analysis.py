import json
import pytest
import websocket
from pprint import pprint


@pytest.mark.usefixtures('init')
class TestAnalysis():

    payload = {
        'index': 'logs',
        'key_words': {
            'pod.name': 'qingcloud-autotest-2951-5aa237ae-7d6e-46a4-bbd6-423110ea0231',
            'container.name': 'aomaker',
            # 'kubernetes.labels.uid': '091143e5-464e-4704-8438-04ecc98f4b1a',
        },
        "from_": 0,
        "size": 200,
    }

    def test_es_log(self):
        resp = self.bs.post(
            f'{self.url}/analysis/raw',
            json=self.payload
        )
        pprint(resp.json())
        assert resp.status_code == 200

        self.payload['offset'] = resp.json()['offset']
        ws = websocket.WebSocket()
        ws.connect(
            f'{self.ws_url}/analysis/ws/raw',
        )
        ws.send(json.dumps(self.payload))
        resp = ws.recv()
        pprint(json.loads(resp))
        assert ws.status == 101
