from phdkit.log import LogOutput, EmailNotifier
from phdkit.configlib import config
import click
from .agent import Agent, logger as agent_logger


@click.command()
@click.option("--develop", is_flag=True, help="Enable in-development mode.", default=True)
def main(develop: bool) -> None:
    if not develop:
        email_notifier = EmailNotifier()
        config[email_notifier].load("watchcat.config.toml", "watchcat.env.toml")
        agent_logger.add_output(LogOutput.email(email_notifier))

    agent = Agent()
    config[agent].load("watchcat.config.toml", "watchcat.env.toml")

    papers = agent.fetch_papers()
    for paper in papers:
        agent.worth_reading(paper)
