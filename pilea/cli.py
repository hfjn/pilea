from pathlib import Path
import time

import click
from click import ClickException, Context, pass_context
from livereload import Server

from pilea.build_controller import BuildController
from pilea.state import State, pass_state
from shutil import copytree
import os

EXECUTION_PATH = Path(os.getcwd())
INPUT_FOLDER = Path(__file__).parent / "input" 

@click.group(help="pilea - a tiny static site generator.")
def pilea():
    pass


@pilea.command()
@click.argument("folder")
def new(folder):
    """Creates basic folder structure to work with pilea.
    \b
    USAGE:
    \b
    pilea new FOLDER        : Creates new project at FOLDER
    """
    folder = EXECUTION_PATH / folder
    if folder.exists():
        raise ClickException(f"{folder} already exists.")
    folder.mkdir()
    copytree(INPUT_FOLDER, folder / "input")
    click.echo(f"Created folder at {folder}")


@pilea.command()
@pass_state
def build(state: State, watch: bool):
    """
    Compiles the input files. Has to be run from within the project folder.
    Resulting files will be in site/
    
    USAGE:

    pilea build        : Will compile the static site to site/
    """
    build_controller = BuildController(state)
    build_controller.build_all()


@pilea.command()
@pass_state
@pass_context
def serve(ctx: Context, state: State):
    """
    Starts a simple development server with live-reload functionality. 
    
    USAGE:

    pilea serve        : Will serve the static site at localhost:5050
    """
    build_controller = BuildController(state)
    build_controller.build_all()
    server = Server()
    server.watch(f"{str(state.input_folder)}/**/*.html", build_controller.build_all)
    server.watch(f"{str(state.input_folder)}/**/**/*.md", build_controller.build_all)
    server.watch(f"{str(state.input_folder)}/**/*.css", build_controller.build_css)
    server.serve(root=state.output_folder)
