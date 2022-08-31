import pytest
import websocket
from loguru import logger


@pytest.mark.usefixtures('init')
class TestAnalysis():

    header = {
        "Authorization": "admin"
    }

    def test_msg(self):
        resp = self.bs.get('/analysis/raw/demo-1', headers=self.header)
        assert resp.status_code == 200

    def test_ws(self):
        ws = websocket.WebSocket()
        ws.connect(
            "ws://tink.test:31695/analysis/ws/demo-1",
            header=self.header
        )
        ws.send("1")
        resp = ws.recv()
        logger.info(resp)
        assert ws.status == 101
        assert 'offset' in resp
