import pytest


@pytest.mark.usefixtures('init')
class TestController():

    def test_file_list(self):
        resp = self.bs.post('/analysis')
        assert resp.status_code == 200
