import time
from threading import Thread
from vk_bot.settings import *
from vk_bot.local_bot import LocalBot
from vk_bot.chat_bot import ChatBot


local_bot = LocalBot()
chat_bot = ChatBot()


def check() -> None:
    while True:
        local_bot.parse()
        local_bot.push_post()
        time.sleep(TIME_UPDATE_MINUTES * 60)


def vk() -> None:
    b_l = Thread(target=local_bot.start)
    b_c = Thread(target=chat_bot.start)
    parser = Thread(target=check)
    b_l.start()
    b_c.start()
    parser.start()


if __name__ == '__main__':
    vk()
