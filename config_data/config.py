from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str


@dataclass
class Config:
    tg_bot: TgBot
    payment_token: str

    gigachat_token: str


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(token=env('BOT_TOKEN')),
                  gigachat_token=env('GIGACHAT_TOKEN'),
                  payment_token=env('PAYMENT_TOKEN'))
