import json
import time
import websocket
from requests import Session


class TestAnalysis:

    bs = Session()
    bs.headers["Authorization"] = "admin"
    bs.headers["x_atop_version"] = "dev"

    # url = f"http://127.0.0.1:8005"
    # ws_url = f"http://127.0.0.1:8005"
    url = f"http://172.16.60.10:31690/apis/analysis"
    ws_url = f"ws://172.16.60.10:31690/apis/analysis"

    payload = {
        "index": "logs",
        "key_words": {
            "kubernetes.labels.uid": "4bf580d6-53e1-4cf0-b0ef-1ec9b675e3f31",
            "kubernetes.labels.app": "aomaker",
            # "log.file.path": f"/hatbox/Log/logs/hatbox.log",
        },
        "from_": 0,
        "size": 20,
        # "offset": [1717113612433],
        # "offset": [1717116041813],
    }

    def test_http_log(self):
        resp = self.bs.post(f"{self.url}/logs", json=self.payload)
        assert resp.status_code == 200

    def test_ws_log(self):
        headers = {"Authorization": "admin", "x-atop-version": "1.0.10"}
        ws = websocket.create_connection(f"{self.ws_url}/logs/ws", header=headers)
        while True:
            ws.send(json.dumps(self.payload))
            resp = ws.recv()
            assert ws.status == 101
            resp = json.loads(resp)
            self.payload["offset"] = resp.get("offset")
            time.sleep(30)
