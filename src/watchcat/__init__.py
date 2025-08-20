import click
from phdkit import unimplemented


@click.command()
@click.option("--develop/--prod", help="Enable in-development mode.", default=True)
@click.option("--archive-email/--no-archive-email", help="Archive processed emails.", default=False, show_default=True)
def main(develop: bool, archive_email: bool) -> None:
    unimplemented()
