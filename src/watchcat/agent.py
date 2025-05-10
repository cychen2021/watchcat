from phdkit.configlib import configurable, setting, ConfigReader

def __read_config(config_file: str | None = None):
    with open(config_file if config_file is not None else "config.toml", "r") as f:
        return {} # TODO: Implement config reading logic

@configurable(__read_config)
class Agent:
    pass