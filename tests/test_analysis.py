import pytest


@pytest.mark.usefixtures('init')
class TestAnalysis():

    def test_metrics(self):
        resp = self.bs.get('/metrics')
        assert resp.status_code == 200

    def test_sub_msg(self):
        resp = self.bs.get('/analysis/kafak/demo-1')
        assert resp.status_code == 200
