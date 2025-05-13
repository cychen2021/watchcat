from phdkit.log import LogOutput, EmailNotifier
from phdkit.configlib import config
from .agent import Agent, logger as agent_logger


def main() -> None:
    email_notifier = EmailNotifier()
    config[email_notifier].load("watchcat.config.toml", "watchcat.env.toml")
    agent_logger.add_output(LogOutput.email(email_notifier))

    agent = Agent()
    config[agent].load("watchcat.config.toml", "watchcat.env.toml")

    papers = agent.fetch_papers()
    for paper in papers:
        agent.worth_reading(paper)
