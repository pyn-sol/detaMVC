from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from {obj}.model import {Obj}


{obj}_router = APIRouter()
templates = Jinja2Templates(directory="")


# INDEX
@{obj}_router.get('/')
def index(request: Request):
    {obj}_list = {Obj}.get_all()
    return templates.TemplateResponse(
        '{obj}/templates/index.html',
        context={{'request': request, '{obj}_list': {obj}_list }})

# CREATE
@{obj}_router.get('/new')
def new(request: Request):
    return templates.TemplateResponse(
        '{obj}/templates/form.html',
        context={{'request': request, 'vals': dict() }})

@{obj}_router.post('/new', response_model={Obj})
async def create(request: Request):
    form_data = await request.form()
    {obj} = {Obj}.parse_obj(form_data)
    {obj}.save()
    return view(request, {obj}.key)

# UPDATE
@{obj}_router.get('/edit/{{key}}')
def edit(request: Request, key: str):
    vals = {Obj}.get(key)
    return templates.TemplateResponse(
        '{obj}/templates/form.html',
        context={{'request': request, 'vals': vals.dict() }})

@{obj}_router.post("/edit/{{key}}")
async def update(request: Request, key: str):
    stored_data = {Obj}.get(key)
    update_data = await request.form()
    parsed = {Obj}.parse_obj(update_data).dict(exclude_unset=True)
    parsed['key'] = key
    updated = stored_data.copy(update=parsed)
    updated.save()
    return view(request, key)

# DELETE
@{obj}_router.get('/delete/{{key}}')
def delete(request: Request, key: str):
    {Obj}.delete_key(key)
    return index(request)

# VIEW
@{obj}_router.get('/{{key}}')
def view(request: Request, key: str):
    {obj} = {Obj}.get(key)
    return templates.TemplateResponse(
        '{obj}/templates/view.html',
        context={{'request': request, '{obj}': {obj} }})

