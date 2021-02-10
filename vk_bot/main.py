import logging
import os
import random
import time
from threading import Thread

import requests
import vk_api
from vk_api.longpoll import VkEventType

from vk_bot.polls import MyVkLongPoll, MyVkBotLongPoll


class LocalBot:
    def __init__(self):
        self.token = os.getenv('TOKEN')
        self.vk_session = vk_api.VkApi(token=self.token)
        self.vk = self.vk_session.get_api()
        self.long = MyVkLongPoll(self.vk_session)

    def send_message(self, user_id, message):
        path = r'button.json'
        while True:
            try:
                self.vk.messages.send(user_id=user_id, random_id=random.getrandbits(32), message=message,
                                      keyboard=open(path, "r", encoding="UTF-8").read())
                break
            except Exception as e:
                print(e)
                time.sleep(10)

    def commands(self, event):
        if event.text.lower() == 'помощь' or event.text.lower() == 'help' or event.text.lower() == 'начать':
            self.send_message(user_id=event.user_id, message='Приветики, я бот-информатор)')
        elif event.text.lower() == 'меню':
            self.send_message(event.user_id, 'Меню!')

    def bot(self):
        try:
            while True:
                for event in self.long.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        if event.from_user:  # Если написали в ЛС
                            if event.text:
                                self.commands(event)
        except requests.exceptions.ReadTimeout:
            time.sleep(10)
        except vk_api.AuthError as error_msg:
            logger.exception('Auth')
            print('ERROR:', error_msg)
        except Exception as e:
            print(f'Получена ошибка: {e}\n')
            time.sleep(10)


logger = logging.getLogger(__name__)
f_handler = logging.FileHandler(r'bot_crash.log')
f_handler.setLevel(logging.ERROR)
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
f_handler.setFormatter(f_format)
logger.addHandler(f_handler)
bot = LocalBot()


if __name__ == '__main__':
    b_l = Thread(target=bot.bot)
    b_l.start()
