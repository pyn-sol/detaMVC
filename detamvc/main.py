import typer
import os
from detamvc import __version__
from .generator import build_base, gen_scaffold
from typing import List
from . import utilities as utils

app = typer.Typer()


@app.command()
def version():
    """ show current version of DetaMVC"""
    typer.echo(f"DetaMVC {__version__}")

@app.command()
def new(project: str):
    """ create a new project """
    new_folder = os.path.join(os.curdir, project)
    try:      
        typer.secho(f"\nBuilding new project: {project}\n", fg='green')
        build_base(new_folder, project)
        typer.echo(f"\n{project} was created.\n")
    except FileExistsError:
        typer.secho(f"'{project}' already exists in this folder.\n", fg='red')

@app.command()
def server():
    """ run the app locally """
    os.system("uvicorn main:app --reload")

@app.command()
def s():
    """ alias for 'server' """
    server()

@app.command()
def scaffold(obj: str, attributes: List[str]):
    """ create a router and views for a described object """
    typer.secho(f"\nScaffolding views and router for: {obj}\n", fg='green')
    gen_scaffold(os.curdir, obj, attributes)
    typer.echo(f"\n{obj} was created.\n")

@app.command()
def set_project_key(project_key: str):
    """ set your development project key for Deta for faster builds """
    utils.set_project_key(project_key)
    typer.secho("Project Key successfully set.", fg='green')

@app.command()
def clear_project_key():
    """ clear your Deta development project key """
    utils.clear_project_key()
    typer.secho("Project Key successfully cleared.", fg='green')

@app.command()
def view_config():
    """ view your development configurations """
    conf = utils.config()
    typer.echo(conf)

