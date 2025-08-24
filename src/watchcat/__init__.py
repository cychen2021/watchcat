import click
from xdg_base_dirs import xdg_config_home
from phdkit import unimplemented
from phdkit.configlib import configurable, setting, TomlReader, config

@configurable(
    TomlReader("watchcat.config.toml"),
    load_env=TomlReader("watchcat.env.toml")
)
class App:
    @setting("email.provider")
    def email_provider(self) -> str: ...

    @setting("email.address")
    def email_address(self) -> str: ...

    @setting("email.password")
    def email_password(self) -> str: ...

    def run(self):
        unimplemented()

@click.command()
@click.option("--develop/--prod", help="Enable in-development mode.", default=True)
@click.option(
    "--archive-email/--no-archive-email",
    help="Archive processed emails.",
    default=False,
    show_default=True,
)
def main(develop: bool, archive_email: bool) -> None:
    app = App()
    config[app].load()