import pytest


@pytest.mark.usefixtures('init')
class TestController():

    def test_file_list(self):
        resp = self.bs.post('/analysis')
        assert resp.status_code == 200

    def test_get_kafka(self):
        resp = self.bs.get('/analysis/kafak')
        assert resp.status_code == 200
