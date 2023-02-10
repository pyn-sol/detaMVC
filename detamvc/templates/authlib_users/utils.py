from datetime import datetime, timedelta
from functools import wraps

from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse
import jwt
from passlib.context import CryptContext
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config


def current_user(request: Request):
    user = request.session.get('user')
    return user


def authenticated_path(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = current_user(kwargs['request'])
        if not user:
            return RedirectResponse('/user/not_authenticated', 303)
        return func(*args, **kwargs)
    return wrapper


class Auth():
    config = Config('.env')
    hasher= CryptContext(schemes=['bcrypt'])
    secret = config.get("APP_SECRET")

    # GOOGLE OAUTH
    """
    Configuring Google Auth2.0 API Client:

    https://developers.google.com/identity/oauth2/web/guides/get-google-api-clientid
    click on 'configure a project'
    """

    oauth = OAuth(config)

    oauth.register(
        name='google',
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={{
            'scope': 'openid email profile'
        }}
    )
    # ============

    def encode_password(self, password):
        return self.hasher.hash(password)

    def verify_password(self, password, encoded_password):
        return self.hasher.verify(password, encoded_password)

    def encode_token(
        self,
        username,
        scope='access_token',
        exp=datetime.utcnow() + timedelta(days=14)):

        payload = {{
            'exp' : exp,
            'iat' : datetime.utcnow(),
                'scope': scope,
            'sub' : username
        }}

        encoded = jwt.encode(
            payload,
            self.secret,
            algorithm='HS256'
        )
        if isinstance(encoded, bytes):
            encoded = encoded.decode('utf-8')
        return encoded

    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            if (payload['scope'] == 'access_token'):
                return payload['sub']
            raise HTTPException(status_code=401, detail='Scope for the token is invalid')
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Token expired')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid token')

    def encode_refresh_token(self, username):
        return self.encode_token(
            username,
            scope='refresh_token',
            exp=datetime.utcnow() + timedelta(days=30))

    def refresh_token(self, refresh_token):
        try:
            payload = jwt.decode(refresh_token, self.secret, algorithms=['HS256'])
            if (payload['scope'] == 'refresh_token'):
                username = payload['sub']
                new_token = self.encode_token(username)
                return new_token
            raise HTTPException(status_code=401, detail='Invalid scope for token')
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Refresh token expired')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid refresh token')

    @classmethod
    def is_google_oauth2_enabled(cls):
        if all([cls.config.get('GOOGLE_CLIENT_ID'),
                cls.config.get('GOOGLE_CLIENT_SECRET')]):
            return True
        return False
