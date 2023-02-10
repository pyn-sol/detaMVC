from authlib.integrations.starlette_client import OAuthError
from detamvc.model import Alert
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from user.model import User
from user.utils import current_user, authenticated_path, Auth


user_router = APIRouter()
templates = Jinja2Templates(directory="")


# SIGNUP
@user_router.get('/signup')
def signup_form(request: Request):
    return templates.TemplateResponse(
        'user/templates/signup.html',
        context={{'request': request }})


@user_router.post('/signup')
async def signup(request: Request):
    form_data = await request.form()
    user = User.parse_obj(form_data)
    response = user.signup()
    return templates.TemplateResponse(
        'user/templates/login.html',
        context={{'request': request, 'alert': response}})


#LOGIN
@user_router.get('/login')
def login_form(request: Request):
    continue_with_google = Auth.is_google_oauth2_enabled()
    return templates.TemplateResponse(
        'user/templates/login.html',
        context={{'request': request, 'continue_with_google': continue_with_google}})


@user_router.post('/login')
async def login(request: Request):
    form_data = await request.form()
    potential_user = User.parse_obj(form_data)
    result = potential_user.login(request)
    if isinstance(result, Alert):
        return templates.TemplateResponse(
        'user/templates/login.html',
        context={{'request': request, 'alert': result}})
    else:
        return result


@user_router.get('/dashboard')
@authenticated_path
def dashboard(request: Request):
    return templates.TemplateResponse(
        'user/templates/dashboard.html',
        context={{'request': request, 'user': current_user(request) }})


@user_router.get('/not_authenticated')
def not_authenticated(request: Request):
    return templates.TemplateResponse(
        'user/templates/not_authenticated.html',
        context={{'request': request}})


@user_router.get('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')


@user_router.get('/refresh_token')
@authenticated_path
def refresh_token(request: Request):
    return {{'access_token': User.refresh_token(request)}}


@user_router.get('/username_available')
def username_available(u: str):
    return False if User.fetch_user(u) else True


# GOOGLE OAUTH
@user_router.get('/google_login')
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    return await Auth.oauth.google.authorize_redirect(request, redirect_uri)


@user_router.get('/auth')
async def auth(request: Request):
    try:
        token = await Auth.oauth.google.authorize_access_token(request)
    except OAuthError as error:
        return HTMLResponse(f'<h1>{{error.error}}</h1>')
    user = token.get('userinfo')
    if user:
        db_user = User.signup_from_google_login(user.email)
        request.session['user'] = db_user.dict()
        request.session['user'].update(dict(user))

    return RedirectResponse(url='/user/dashboard')
