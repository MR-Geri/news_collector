import random
import time
from vk_api.bot_longpoll import VkBotEventType

from utils_base import get_base
from vk_bot.settings import *
import requests
import vk_api
from vk_bot.polls import MyVkBotLongPoll


class ChatBot:
    def __init__(self):
        self.token = TOKEN
        self.vk_session = vk_api.VkApi(token=self.token)
        self.vk = self.vk_session.get_api()
        self.long = MyVkBotLongPoll(self.vk_session, ID_GROUP)
        self.help = 'Я могу присылать вам все новые новости из группы, просто включите меня!'

    def send_message(self, chat_id, message, attachment: str = ''):
        self.vk.messages.send(chat_id=chat_id, random_id=random.getrandbits(32), message=message,
                              keyboard=open('chat_bot.json', "r", encoding="UTF-8").read(), attachment=attachment)

    def commands(self, event):
        if event.object.text.lower() == '!help' or event.object.text.lower() == '!помощь':
            self.send_message(chat_id=event.chat_id, message=self.help)
        elif 'включить рассылку' in event.object.text.lower():
            with get_base(True) as base:
                id_ = base.execute("""SELECT * FROM chat_vk WHERE chat_id = ?;""", (event.chat_id,)).fetchall()
                if id_:
                    base.execute("""UPDATE chat_vk SET flag = 1 WHERE chat_id = ?;""", (event.chat_id,))
                else:
                    base.execute("""INSERT INTO chat_vk (id, chat_id, flag)
                                    VALUES((SELECT id FROM chat_vk ORDER BY id DESC LIMIT 1) + 1, ?, ?);""",
                                 (event.chat_id, 1))
            self.send_message(chat_id=event.chat_id, message='Рассылка включена!')
        elif 'выключить рассылку' in event.object.text.lower():
            with get_base(True) as base:
                id_ = base.execute("""SELECT * FROM chat_vk WHERE chat_id = ?;""", (event.chat_id,)).fetchall()
                if id_:
                    base.execute("""UPDATE chat_vk SET flag = 0 WHERE chat_id = ?;""", (event.chat_id,))
                    self.send_message(chat_id=event.chat_id, message='Рассылка выключена!')
                else:
                    self.send_message(chat_id=event.chat_id, message='Вы не подключали рассылку!')

    def start(self):
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
            print('ERROR:', error_msg)
