import os
import pytest

from requests_toolbelt.sessions import BaseUrlSession


TEST_ENV = os.getenv('TEST_ENV')
if TEST_ENV == 'local':
    url = 'http://127.0.0.1:8005'
elif TEST_ENV == 'apisix':
    url = 'http://tink.test:31695'
else:
    url = 'http://tink.com:31693'


@pytest.fixture()
def init(request):
    bs = BaseUrlSession(base_url=url)
    request.cls.bs = bs
