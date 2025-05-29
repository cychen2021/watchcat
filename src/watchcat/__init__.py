from phdkit.log import LogOutput, EmailNotifier, LogLevel
from phdkit.configlib import config
import click
import platform
import os
import xdg_base_dirs as xdg
from datetime import datetime, UTC
from .agent import Agent, logger as agent_logger


@click.command()
@click.option(
    "--develop", is_flag=True, help="Enable in-development mode.", default=True
)
def main(develop: bool) -> None:
    timestamp = datetime.now(UTC).strftime("%Y-%m-%d_%H:%M:%S")
    if not develop:
        email_notifier = EmailNotifier()
        config[email_notifier].load("watchcat/watchcat.config.toml", "watchcat/watchcat.env.toml")
        agent_logger.add_output(LogOutput.email(email_notifier, level=LogLevel.WARNING))
    agent_logger.add_output(LogOutput.stderr())
    if platform.system() == "Windows":
        appdata = os.getenv("LOCALAPPDATA")
        assert appdata is not None, "LOCALAPPDATA is not set"
        log_path = os.path.realpath(
            os.path.join(appdata, f"watchcat_{timestamp}.jsonl")
        )
    else:
        log_path = os.path.realpath(
            os.path.join(xdg.xdg_state_home(), f"watchcat_{timestamp}.jsonl")
        )
    agent_logger.add_output(
        LogOutput.file(log_path, level=LogLevel.DEBUG, format="jsonl")
    )

    agent = Agent()
    config[agent].load("watchcat/watchcat.config.toml", "watchcat/watchcat.env.toml")

    papers = agent.fetch_papers()
    for paper in papers:
        agent.worth_reading(paper)
