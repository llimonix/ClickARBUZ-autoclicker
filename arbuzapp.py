import time, sys, random, requests
from loguru import logger

logger.remove()
logger.add(sys.stdout, colorize=True,
           format="<bold>[ArbuzApp]</bold> <white>{time:YYYY-MM-DD HH:mm:ss.SSS}</white> <red>|</red> <level>{level: <8}</level> <red>|</red> <level>{message}</level>")

TELEGRAM_CHAT_ID = ''
TELEGRAM_BOT_TOKEN = ''

class ArbuzApp():
    def __init__(self):
        self.base_url = 'https://arbuz.betty.games/api'
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 YaBrowser/79.0.3945.117 Safari/537.36',
            'x-telegram-init-data': 'PASTE_SESSION',
        }
        self.proxy = {
            'https': 'http://user:pass@ip:port',
            'http': 'http://user:pass@ip:port''
        }

    def click(self):
        response = requests.post(f'{self.base_url}/click', headers=self.headers,
                                 json={'count': random.randint(25, 35)}, proxies=self.proxy)
        json_data = response.json()

        return json_data.get("code"), json_data.get("count"), json_data.get("currentEnergy")

    def me_info(self):
        response = requests.get(f'{self.base_url}/users/me', headers=self.headers, proxies=self.proxy)
        json_data = response.json()

        return json_data.get("clicks"), json_data.get("energyBoostSum"), json_data.get("energyLimit")

def send_telegram_message(message):
    try:
        response = requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", params={
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
        })
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Не удалось отправить сообщение в Telegram: {e}")

def start():
    coins, energyBoost, energyLimit = app.me_info()
    timeSleep = int(energyLimit / energyBoost)
    message = (f"Status Info\n"
              f"{fcoin(coins)} COINS\n"
              f"{energyBoost} EB\n"
              f"{energyLimit} EL\n"
              f"{timeSleep} sec. TS")
    logger.info(message)
    send_telegram_message(message)

    return timeSleep

def fcoin(number):
    if number < 1000:
        return str(number)
    elif number < 1000000:
        return f"{number / 1000:.1f}K"
    elif number < 1000000000:
        return f"{number / 1000000:.3f}M"
    else:
        return f"{number / 1000000000:.3f}B"


if __name__ == "__main__":
    app = ArbuzApp()
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
        except:
            ...

        time.sleep(.7)
