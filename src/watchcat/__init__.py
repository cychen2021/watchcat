from phdkit.log import LogOutput, EmailNotifier, LogLevel
from phdkit.configlib import config
import click
import platform
import os
import xdg_base_dirs as xdg
from datetime import datetime, UTC
import litellm
from .workflow import Automaton

litellm.suppress_debug_info = True


@click.command()
@click.option(
    "--develop", is_flag=True, help="Enable in-development mode.", default=True
)
def main(develop: bool) -> None:
    agent = Agent()
    timestamp = datetime.now(UTC).strftime("%Y-%m-%d_%H:%M:%S")
    if not develop:
        email_notifier = EmailNotifier()
        config[email_notifier].load(
            "watchcat/watchcat.config.toml", "watchcat/watchcat.env.toml"
        )
        agent.logger.add_output(LogOutput.email(email_notifier, level=LogLevel.WARNING))
        agent.logger.add_output(LogOutput.stderr())
    else:
        agent.logger.add_output(LogOutput.stderr(level=LogLevel.DEBUG))
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
    agent.logger.add_output(
        LogOutput.file(log_path, level=LogLevel.DEBUG, format="jsonl")
    )

    config[agent].load("watchcat/watchcat.config.toml", "watchcat/watchcat.env.toml")
    agent.init()

    papers = agent.fetch_papers()
    for paper in papers:
        worth = agent.worth_reading(paper)
        print(f"Paper {paper.id} worth reading: {worth}")
