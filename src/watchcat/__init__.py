import click
from phdkit import unimplemented


@click.command()
@click.option("--develop/--prod", help="Enable in-development mode.", default=True)
def main(develop: bool) -> None:
    unimplemented()
