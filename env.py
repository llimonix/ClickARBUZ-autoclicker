from dataclasses import dataclass
from environs import Env

@dataclass
class Config:
    TELEGRAM_CHAT_ID: str
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_INIT_DATA: str
    PROXY: str
    PROXY_EXISTS: bool

def load_config(path: str = None) -> Config:
    env = Env()
    env.read_env(path)

    return Config(
        TELEGRAM_CHAT_ID=env.str("TELEGRAM_CHAT_ID"),
        TELEGRAM_BOT_TOKEN=env.str("TELEGRAM_BOT_TOKEN"),
        TELEGRAM_INIT_DATA=env.str("TELEGRAM_INIT_DATA"),
        PROXY=env.str("PROXY"),
        PROXY_EXISTS=env.bool("PROXY_EXISTS"),
    )
