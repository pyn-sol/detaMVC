from authlib.integrations.starlette_client import OAuthError
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from {obj}.utils import oauth, authenticated_path, current_user
from {obj}.model import User


user_router = APIRouter()
templates = Jinja2Templates(directory="")


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
        db_user = User.fetch_or_create(user.email)
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
