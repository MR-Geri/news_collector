import logging
import os
import random
import time
from threading import Thread
from vk_bot.settings import *

import requests
import vk_api
from vk_api.longpoll import VkEventType

from vk_bot.polls import MyVkLongPoll, MyVkBotLongPoll


class LocalBot:
    def __init__(self) -> None:
        self.token = os.getenv('TOKEN')
        self.vk_session = vk_api.VkApi(token=self.token)
        self.vk = self.vk_session.get_api()
        self.post_session = vk_api.VkApi(app_id=int(os.getenv('APP_ID')), login=os.getenv('LOGIN'),
                                         password=os.getenv('PASSWORD'), scope='wall', token=os.getenv('ACCESS_TOKEN'))
        self.post = self.post_session.get_api()
        self.data = None
        self.long = MyVkLongPoll(self.vk_session)

    def upload_image(self, path_file: str) -> None:
        upload_url = self.post.photos.getWallUploadServer(group_id=os.getenv('ID_GROUP'))['upload_url']
        request = requests.post(upload_url, files={'photo': open(path_file, 'rb')})
        params = {'server': request.json()['server'],
                  'photo': request.json()['photo'],
                  'hash': request.json()['hash'],
                  'group_id': os.getenv('ID_GROUP')}
        self.data = self.post.photos.saveWallPhoto(**params)

    def post_post(self, path: str) -> None:
        if os.path.exists(path):
            message = ''  # {datetime.datetime.now().strftime("%H:%M:%S")}
            photos = ''
            try:
                with open(path + '/text.txt', encoding='utf-8') as file:
                    message = file.read()
            except FileNotFoundError:
                pass
            try:
                for file in os.listdir(path):
                    if file.split('.')[-1] in IMAGE_EXTENSION:
                        self.upload_image(path + '/' + file)
                        photo_id = self.data[0]['id']
                        photos += f'photo{self.data[0]["owner_id"]}_{photo_id},'
            except Exception as e:
                print(e)
            if message == photos == '':
                print(f'Не получилось вывести пост: {path}')
            else:
                params = {
                    'message': message,
                    'owner_id': '-' + os.getenv('ID_GROUP'),
                    'from_group': '1',
                    'attachments': photos[:-1]
                }
                self.post.wall.post(**params)

    def send_message(self, user_id, message) -> None:
        path = r'button.json'
        while True:
            try:
                self.vk.messages.send(user_id=user_id, random_id=random.getrandbits(32), message=message,
                                      keyboard=open(path, "r", encoding="UTF-8").read())
                break
            except Exception as e:
                print(e)
                time.sleep(10)

    def commands(self, event) -> None:
        if event.text.lower() == 'помощь' or event.text.lower() == 'help' or event.text.lower() == 'начать':
            self.send_message(user_id=event.user_id, message='Приветики, я бот-информатор)')
        elif event.text.lower() == 'меню':
            self.send_message(event.user_id, 'Меню!')
        elif event.text.lower() == 'тест':
            self.post_post('../image_post/post_1')

    def start(self) -> None:
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
        # except Exception as e:
        #     print(f'Получена ошибка: {e}\n')
        #     time.sleep(10)


logger = logging.getLogger(__name__)
f_handler = logging.FileHandler(r'bot_crash.log')
f_handler.setLevel(logging.ERROR)
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
f_handler.setFormatter(f_format)
logger.addHandler(f_handler)
bot = LocalBot()


def vk() -> None:
    b_l = Thread(target=bot.start)
    b_l.start()


if __name__ == '__main__':
    vk()
