from phdkit.log import LogOutput, EmailNotifier
from phdkit.configlib import Config
from .agent import Agent, logger as agent_logger


def main() -> None:
    email_notifier = EmailNotifier()
    Config.load(email_notifier, "mailog.config.toml", "mailog.env.toml")
    agent_logger.add_output(LogOutput.email(email_notifier))

    agent = Agent()
    Config.load(agent, "watchcat.config.toml", "watchcat.env.toml")

    papers = agent.fetch_papers()
    for paper in papers:
        agent.worth_reading(paper)
