import pytest


@pytest.mark.usefixtures('init')
class TestAnalysis():

    header = {
        "Authorization": "admin"
    }

    def test_metrics(self):
        resp = self.bs.get('/analysis/metrics', headers=self.header)
        assert resp.status_code == 200

    def test_sub_msg(self):
        resp = self.bs.get('/analysis/raw/demo-1', headers=self.header)
        assert resp.status_code == 200
