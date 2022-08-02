import pytest


@pytest.mark.usefixtures('init')
class TestAnalysis():

    def test_metrics(self):
        resp = self.bs.get('/metrics')
        assert resp.status_code == 200

    def test_get_kafka(self):
        resp = self.bs.get('/analysis/kafak/test-5')
        assert resp.status_code == 200

    def test_sub_kafka(self):
        resp = self.bs.get('/analysis/kafak')
        assert resp.status_code == 200

    def test_metrics(self):
        resp = self.bs.get('/metrics')
        assert resp.status_code == 200
