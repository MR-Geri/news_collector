import logging
import time
from threading import Thread
from vk_bot.chat_bot import ChatBot
from vk_bot.local_bot import LocalBot
from vk_bot.settings import *


logger = logging.getLogger(__name__)
f_handler = logging.FileHandler(r'bot_crash.log')
f_handler.setLevel(logging.ERROR)
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
f_handler.setFormatter(f_format)
logger.addHandler(f_handler)
local_bot = LocalBot()
chat_bot = ChatBot()


def check() -> None:
    while True:
        local_bot.parse()
        local_bot.push_post()
        time.sleep(TIME_UPDATE_MINUTES * 60)


def vk() -> None:
    b_l = Thread(target=local_bot.start)
    parser = Thread(target=check)
    b_l.start()
    parser.start()


if __name__ == '__main__':
    vk()
