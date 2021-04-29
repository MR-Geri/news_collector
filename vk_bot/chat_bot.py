import os
import random
import time
from vk_api.bot_longpoll import VkBotEventType
from vk_bot.main import logger
from vk_bot.settings import *
import requests
import vk_api
from vk_bot.polls import MyVkBotLongPoll


class ChatBot:
    def __init__(self):
        self.token = os.getenv('TOKEN_GROUP')
        self.vk_session = vk_api.VkApi(token=self.token)
        self.vk = self.vk_session.get_api()
        self.long = MyVkBotLongPoll(self.vk_session, ID_GROUP)
        self.help = 'Для получения информации с вики напишите:\n!Вики {запрос}'

    def send_message(self, chat_id, message):
        path = r'data/buttons_chats.json'
        self.vk.messages.send(chat_id=chat_id, random_id=random.getrandbits(32), message=message,
                              keyboard=open(path, "r", encoding="UTF-8").read())

    def commands(self, event):
        if event.object.text.lower() == '!help' or event.object.text.lower() == '!помощь':
            self.send_message(chat_id=event.chat_id, message=self.help)
        elif 'меню' in event.object.text.lower():
            self.send_message(chat_id=event.chat_id, message='Меню!')

    def chat_bot(self):
        try:
            while True:
                for event in self.long.listen():
                    if event.type == VkBotEventType.MESSAGE_NEW:
                        if event.object.peer_id != event.object.from_id:
                            if event.object.text:
                                self.commands(event)
        except requests.exceptions.ReadTimeout:
            time.sleep(10)
        except vk_api.AuthError as error_msg:
            logger.exception('Auth')
            print('ERROR:', error_msg)
