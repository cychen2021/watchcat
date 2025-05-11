from phdkit.log import LogOutput, EmailNotifier
from .agent import Agent, logger as agent_logger


def main() -> None:
    email_notifier = EmailNotifier()
    email_notifier.load_config("mailog.config.toml", "mailog.env.toml")
    agent_logger.add_output(LogOutput.email(email_notifier))

    agent = Agent()
    agent.load_config("watchcat.config.toml", "watchcat.env.toml")

    papers = agent.fetch_papers()
    for paper in papers:
        agent.worth_reading(paper)
