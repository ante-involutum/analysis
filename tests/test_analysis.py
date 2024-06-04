import json
import pytest
import websocket


@pytest.mark.usefixtures("init")
class TestAnalysis:

    payload = {
        "index": "logs",
        "key_words": {
            "pod.name": "qingcloud-autotest-task4557",
            "container.name": "aomaker",
        },
        "from_": 0,
        "size": 200,
        # "offset": [1717113612433],
        # "offset": [1717116041813],
    }

    def test_http_log(self):
        resp = self.bs.post(f"{self.url}/analysis/raw", json=self.payload)
        assert resp.status_code == 200

    def test_ws_log(self):
        ws = websocket.WebSocket()
        ws.connect(f"{self.ws_url}/analysis/ws/raw")
        while True:
            ws.send(json.dumps(self.payload))
            resp = ws.recv()
            assert ws.status == 101
            resp = json.loads(resp)
            self.payload['offset'] = resp.get('offset')
