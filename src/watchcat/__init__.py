import click
from phdkit import unimplemented

@click.command()
@click.option(
    "--develop", is_flag=True, help="Enable in-development mode.", default=True
)
def main(develop: bool) -> None:
    unimplemented()