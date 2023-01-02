from functools import wraps

from authlib.integrations.starlette_client import OAuth
from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.config import Config

"""
Using Authlib with FastAPI:
https://blog.authlib.org/2020/fastapi-google-login

Google Auth API Client:
https://developers.google.com/identity/oauth2/web/guides/get-google-api-clientid
click on 'configure a project'
"""

config = Config('.env')
oauth = OAuth(config)

CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_kwargs={{
        'scope': 'openid email profile'
    }}
)

def current_user(request: Request):
    user = request.session.get('user')
    return user


def authenticated_path(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = current_user(kwargs['request'])
        if not user:
            return RedirectResponse('/{obj}/not_authenticated')
        return func(*args, **kwargs)
    return wrapper
