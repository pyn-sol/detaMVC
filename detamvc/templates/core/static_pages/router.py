from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

static_pages_router = APIRouter()
templates = Jinja2Templates(directory="")

@static_pages_router.get('/')
def index(request: Request):
    return templates.TemplateResponse(
        'static_pages/templates/index.html',
        context={'request': request })