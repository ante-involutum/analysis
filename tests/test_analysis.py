import pytest


@pytest.mark.usefixtures('init')
class TestAnalysis():

    def test_metrics(self):
        resp = self.bs.get('/analysis/metrics')
        assert resp.status_code == 200

    def test_sub_msg(self):
        resp = self.bs.get('/analysis/raw/demo-1')
        assert resp.status_code == 200
