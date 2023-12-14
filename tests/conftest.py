import os
import pytest
from requests import Session


HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
RELEASE = os.getenv('RELEASE')


@pytest.fixture()
def init(request):
    bs = Session()
    bs.headers['apikey'] = 'admin'
    request.cls.bs = bs
    request.cls.url = f'http://{HOST}:{PORT}/{RELEASE}'
    request.cls.ws_url = f'ws://{HOST}:{PORT}/{RELEASE}'
    # request.cls.url = f'http://{HOST}:{PORT}'
    # request.cls.ws_url = f'ws://{HOST}:{PORT}'
