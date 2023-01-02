import typer
import os
from detamvc import __version__
from .generator import build_base, gen_scaffold, gen_authlib
from typing import List
from . import utilities as utils

app = typer.Typer()


@app.command()
def version():
    """ show current version of DetaMVC"""
    typer.echo(f"DetaMVC {__version__}")

@app.command()
def new(project: str, style: str = "bootstrap"):
    """ create a new project """
    if utils.valid_style(style):
        new_folder = os.path.join(os.curdir, project)
        try:      
            typer.secho(f"\nBuilding new project: {project}\n", fg='green')
            build_base(new_folder, project, style.upper())
            typer.echo(f"\n{project} was created.\n")
        except FileExistsError:
            typer.secho(f"'{project}' already exists in this folder.\n", fg='red')
    else:
        typer.secho(f"'{style}' is not a valid style for a project. Valid options are: {utils.STYLES}", fg='red')

@app.command()
def server():
    """ run the app locally """
    utils.run_server()

@app.command()
def s():
    """ alias for 'server' """
    server()

@app.command()
def build():
    """ alias for mkdocs build """
    os.system("mkdocs build")

@app.command()
def scaffold(obj: str, attributes: List[str]):
    """ create a router and views for a described object """
    if utils.check_project_type() == "MKDOCS":
        typer.secho(f"Scaffolding is not currently supported for MKDOCS styled apps", fg='red')
    else:
        typer.secho(f"\nScaffolding views and router for: {obj}\n", fg='green')
        gen_scaffold(os.curdir, obj, attributes)
        typer.echo(f"\n{obj} was created.\n")

@app.command()
def auth():
    """ generate authorization framework for users """
    if utils.check_project_type() == "MKDOCS":
        typer.secho(f"User Auth is not currently supported for MKDOCS styled apps", fg='red')
    else:
        typer.secho(f"\nGenerating views and router for: User\n", fg='green')
        gen_authlib(os.curdir)
        typer.echo(f"\nAuth was created.\n")

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
