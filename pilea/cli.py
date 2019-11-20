import click
from click import pass_context, Context
from livereload import Server
from pilea.build_controller import BuildController
from pilea.state import pass_state, State
import time
DEFAULT_TEMPLATE = "default.html"


@click.group(help="pilea - a tiny static site generator.", invoke_without_command=True)
def pilea():
    pass


@pilea.command()
@click.option("--watch", type=bool, is_flag=True)
@pass_state
def build(state: State, watch: bool):
    build_controller = BuildController(state)
    build_controller.build_all()


@pilea.command()
@pass_state
@pass_context
def serve(ctx: Context, state: State):
    build_controller = BuildController(state)
    build_controller.build_all()
    server = Server()
    server.watch(f"{str(state.input_folder)}/**/*.html", build_controller.build_all)
    server.watch(f"{str(state.input_folder)}/**/**/*.md", build_controller.build_all)
    server.watch(f"{str(state.input_folder)}/**/*.css", build_controller.build_css)
    server.serve(root=state.output_folder)
