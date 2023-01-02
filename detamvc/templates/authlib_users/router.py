from datetime import date
from functools import wraps

from authlib.integrations.starlette_client import OAuth, OAuthError
from detamvc.model import DetaModel, ItemNotFound
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.config import Config


user_router = APIRouter()
templates = Jinja2Templates(directory="")


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


class User(DetaModel):
    created_date: str

    class Config:
        table_name = "{proj}_{obj}"
    
    @classmethod
    def new_user(cls, email):
        data = {{
            'key': email,
            'created_date': str(date.today())
        }}
        user = User.parse_obj(data)
        user.save()
        return user


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


def fetch_or_create_user(email):
    try:
        user = User.get(email)
    except ItemNotFound: 
        user = User.new_user(email)
    return user


@user_router.get('/login')
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@user_router.get('/auth')
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        return HTMLResponse(f'<h1>{{error.error}}</h1>')
    user = token.get('userinfo')
    if user:
        db_user = fetch_or_create_user(user.email)
        request.session['user'] = db_user.dict()
        request.session['user'].update(dict(user))

    return RedirectResponse(url='/{obj}/dashboard')


@user_router.get('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')


# NOT AUTHENTICATED
@user_router.get('/not_authenticated')
def not_authenticated(request: Request):
    return templates.TemplateResponse(
        '{obj}/templates/not_authenticated.html',
        context={{'request': request}})


# USER LOGGED IN DASH
@user_router.get('/dashboard')
@authenticated_path
def dashboard(request: Request):
    user = current_user(request)
    return templates.TemplateResponse(
        '{obj}/templates/dashboard.html',
        context={{'request': request, 'user': user}})
