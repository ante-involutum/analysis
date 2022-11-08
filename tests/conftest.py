import os
import pytest

from requests_toolbelt.sessions import BaseUrlSession


TEST_ENV = os.getenv('TEST_ENV')
if TEST_ENV == 'dev':
    url = 'http://127.0.0.1:8005'
    ws_url = "ws://127.0.0.1:8005/analysis/ws/raw"
elif TEST_ENV == 'test':
    url = 'http://tink.test:31695'
    ws_url = "ws://tink.test:31695/analysis/ws/raw"


@pytest.fixture()
def init(request):
    bs = BaseUrlSession(base_url=url)
    request.cls.bs = bs
    request.cls.ws_url = ws_url
