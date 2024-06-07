import json
import time
import pytest
import websocket


@pytest.mark.usefixtures("init")
class TestAnalysis:

    payload = {
        "index": "logs",
        "key_words": {
            "pod.name": "qingcloud-autotest-4606-b7b54a3a-ce44-45bf-a9ce-2e2cedcfe014",
            "container.name": "aomaker",
            "labels.uid": "5f20c0eb-26e2-491d-98fd-d6256cb3398a",
        },
        "from_": 0,
        "size": 20,
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
            self.payload["offset"] = resp.get("offset")
            time.sleep(30)
