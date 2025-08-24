import click
from xdg_base_dirs import xdg_config_home
from pathlib import Path
from phdkit import unimplemented
from phdkit.configlib import configurable, setting, TomlReader, config

DEFAULT_CONFIG_FILE = str(Path(xdg_config_home()) / "watchcat" / "config.toml")
DEFAULT_ENV_FILE = str(Path(xdg_config_home()) / "watchcat" / "env.toml")

@configurable(
    TomlReader(DEFAULT_CONFIG_FILE),
    load_env=TomlReader(DEFAULT_ENV_FILE)
)
class App:
    @setting("email.provider")
    def email_provider(self) -> str: ...

    @setting("email.address")
    def email_address(self) -> str: ...

    @setting("email.password")
    def email_password(self) -> str: ...

    @setting("email.archive_processed")
    def email_archive_processed(self) -> bool: ...

    def run(self):
        unimplemented()

@click.command()
@click.option("--develop/--prod", help="Enable in-development mode.", default=True)
@click.option(
    "config_file",
    "--config",
    "-c",
    default=DEFAULT_CONFIG_FILE,
    show_default=True,
    type=click.Path(exists=True)
)
@click.option(
    "env_file",
    "--env",
    "-e",
    default=DEFAULT_ENV_FILE,
    show_default=True,
    type=click.Path(exists=True)
)
def main(develop: bool, config_file: str, env_file: str) -> None:
    app = App()
    config[app].load(config_file, env_file)