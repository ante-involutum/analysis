import pytest


@pytest.mark.usefixtures('init')
class TestAnalysis():

    def test_metrics(self):
        resp = self.bs.get('/metrics')
        assert resp.status_code == 200

    def test_sub_msg(self):
        resp = self.bs.get('/analysis/raw/jmeter-3')
        assert resp.status_code == 200

    def test_es_msg(self):
        resp = self.bs.get('/analysis/attributes/', json={
            'job_type': 'demo',
            'job_name': '3',
            'from_': 0,
            'size': 20,
        })
        assert resp.status_code == 200
