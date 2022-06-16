import os
import pytest

from requests_toolbelt.sessions import BaseUrlSession


TEST_ENV = os.getenv('TEST_ENV')
if TEST_ENV == 'local':
    url = 'http://127.0.0.1:8005'
else:
    url = 'http://tink.com:31695'


@pytest.fixture()
def init(request):
    bs = BaseUrlSession(base_url=url)
    request.cls.bs = bs
