import time
import sys
import random
import requests
from loguru import logger

from env import load_config

logger.remove()
logger.add(sys.stdout, colorize=True,
           format="<bold>[ArbuzApp]</bold> <white>{time:YYYY-MM-DD HH:mm:ss.SSS}</white> <red>|</red> <level>{level: <8}</level> <red>|</red> <level>{message}</level>")

class ArbuzApp:
    def __init__(self) -> None:
        self.config = load_config('config.env')
        self.base_url: str = 'https://arbuz.betty.games/api'
        self.headers: dict = {
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/79.0.3945.117 YaBrowser/79.0.3945.117 Safari/537.36',
            'x-telegram-init-data': self.config.TELEGRAM_INIT_DATA,
        }
        self.proxy: dict = self.get_proxy()

    def get_proxy(self) -> dict:
        if self.config.PROXY_EXISTS:
            return {'https': f'http://{self.config.PROXY}', 'http': f'http://{self.config.PROXY}'}

        return {'https': '', 'http': ''}

    def click(self) -> tuple[str, int, float]:
        response = requests.post(
            f'{self.base_url}/click/apply',
            headers=self.headers,
            json={'count': random.randint(25, 35)},
            proxies=self.proxy,
            timeout=10
        )
        json_data = response.json()

        return json_data.get("code"), json_data.get("count"), json_data.get("currentEnergy")

    def me_info(self) -> tuple[int, float, int]:
        response = requests.get(f'{self.base_url}/users/me', headers=self.headers, proxies=self.proxy, timeout=10)
        json_data = response.json()

        return json_data.get("clicks"), json_data.get("energyBoostSum"), json_data.get("energyLimit")

app = ArbuzApp()

def send_telegram_message(message: str) -> None:
    try:
        response = requests.get(f"https://api.telegram.org/bot{app.config.TELEGRAM_BOT_TOKEN}/sendMessage", params={
            'chat_id': app.config.TELEGRAM_CHAT_ID,
            'text': message,
        }, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        logger.error("Не удалось отправить сообщение в Telegram")


def start() -> int:
    coins, energy_boost, energy_limit = app.me_info()
    time_sleep = int(energy_limit / energy_boost)
    message = (f"Status Info\n"
               f"{fcoin(coins)} COINS\n"
               f"{energy_boost} EB\n"
               f"{energy_limit} EL\n"
               f"{time_sleep} sec. TS")
    logger.info(message)
    send_telegram_message(message)

    return time_sleep


def fcoin(number: float) -> str:
    if number < 1000:
        return str(number)
    if number < 1000000:
        return f"{number / 1000:.1f}K"
    if number < 1000000000:
        return f"{number / 1000000:.3f}M"
    if number < 1000000000000:
        return f"{number / 1000000000:.3f}B"

    return f"{number / 1000000000000:.3f}T"


if __name__ == "__main__":
    timeSleep = start()

    while True:
        try:
            error, click, energy = app.click()
            if error is not None:
                if error == "NOT_ENOUGH_ENERGY":
                    timeSleep = start()
                    time.sleep(timeSleep)
                else:
                    logger.error(error)
                    time.sleep(10)
            else:
                logger.success(f"+{click} COINS | {energy} ENERGY")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")

        time.sleep(0.7)
