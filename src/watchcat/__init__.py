import click
from xdg_base_dirs import xdg_config_home, xdg_data_home
from pathlib import Path
from phdkit import unimplemented
from phdkit.log import Logger, LogOutput, LogLevel, LogOutputKind
from phdkit.configlib import configurable, setting, TomlReader, config

DEFAULT_CONFIG_FILE = str(Path(xdg_config_home()) / "watchcat" / "config.toml")
DEFAULT_ENV_FILE = str(Path(xdg_config_home()) / "watchcat" / "env.toml")
DEFAULT_STORE_FILE = str(Path(xdg_data_home()) / "watchcat" / "store.db")


@configurable(TomlReader(DEFAULT_CONFIG_FILE), load_env=TomlReader(DEFAULT_ENV_FILE))
class App:
    def __init__(self) -> None:
        self._logger = None
        self.pop_server = None
        self.pop_port = None
        self.pop_require_ssl = True

    @setting("email.provider")
    def email_provider(self) -> str: ...

    @setting("email.address")
    def email_address(self) -> str: ...

    @setting("email.password")
    def email_password(self) -> str: ...

    @setting("email.archive_processed", default=False)
    def email_archive_processed(self) -> bool: ...

    @setting("store.db_file", default=DEFAULT_STORE_FILE)
    def store_db_file(self) -> str: ...

    @setting("log.level", default="INFO")
    def log_level(self) -> str: ...

    @property
    def logger(self) -> Logger:
        if self._logger is None:
            match self.log_level:
                case "INFO":
                    level = LogLevel.INFO
                case "DEBUG":
                    level = LogLevel.DEBUG
                case "WARNING":
                    level = LogLevel.WARNING
                case "ERROR":
                    level = LogLevel.ERROR
                case "CRITICAL":
                    level = LogLevel.CRITICAL
                case _:
                    raise ValueError(f"Invalid log level: {self.log_level}")
            output = LogOutput("MainApp.default", kind=LogOutputKind.CONSOLE, level=level)
            self._logger = Logger("MainApp", outputs=[output])
        return self._logger

    def run(self, steps=["pull", "summarize", "analyze", "evaluate"]):
        match self.email_provider:
            case "gmail":
                self.pop_server = "pop.gmail.com"
                self.pop_port = 995
                self.pop_require_ssl = True
                self.logger.debug("Email set up - Gmail", {"server": self.pop_server, "port": self.pop_port, "ssl": self.pop_require_ssl})
            case _:
                raise ValueError(f"Invalid email provider: {self.email_provider}")
        unimplemented()


@click.command()
@click.option("--develop/--prod", help="Enable in-development mode.", default=True, hidden=True)
@click.option("--steps", default="pull,summarize,analyze,evaluate", hidden=True)
@click.option(
    "config_file",
    "--config",
    "-c",
    default=DEFAULT_CONFIG_FILE,
    show_default=True,
    type=click.Path(exists=True),
)
@click.option(
    "env_file",
    "--env",
    "-e",
    default=DEFAULT_ENV_FILE,
    show_default=True,
    type=click.Path(exists=True),
)
def main(develop: bool, config_file: str, env_file: str, steps: str) -> None:
    app = App()
    config[app].load(config_file, env_file)
    if develop:
        app.log_level = "DEBUG"
    app.run(steps=steps.split(","))
