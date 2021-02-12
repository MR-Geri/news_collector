import json
import logging
import os
import random
import time
from threading import Thread
from vk_bot.settings import *

import requests
import vk_api
from vk_api.longpoll import VkEventType
from parser_posts.parser import Habr

from vk_bot.polls import MyVkLongPoll


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
        #
        self.habr = Habr()

    def upload_image(self, path_file: str = '', url: str = None) -> None:
        upload_url = self.post.photos.getWallUploadServer(group_id=os.getenv('ID_GROUP'))['upload_url']
        if not url:
            photo = open(path_file, 'rb')
        else:
            with open(path_file + url.split('/')[-1], 'wb') as file:
                file.write(requests.post(url).content)
            photo = open(path_file + url.split('/')[-1], 'rb')
        request = requests.post(upload_url, files={'photo': photo})
        params = {'server': request.json()['server'],
                  'photo': request.json()['photo'],
                  'hash': request.json()['hash'],
                  'group_id': os.getenv('ID_GROUP')}
        self.data = self.post.photos.saveWallPhoto(**params)

    def post_post(self, path: str) -> bool:
        if os.path.exists(path):
            message = ''  # {datetime.datetime.now().strftime("%H:%M:%S")}
            photos = ''
            try:
                with open(path + '/text.txt', encoding='utf-8') as file_message:
                    message = file_message.read()
            except FileNotFoundError:
                pass
            try:
                images = None
                with open(path + '/image.txt', encoding='utf-8') as file_images:
                    url_images = file_images.readlines()
            except FileNotFoundError:
                images = os.listdir(path)
                url_images = None
            if images:
                for img in images:
                    if img.split('.')[-1] in IMAGE_EXTENSION:
                        self.upload_image(path + '/' + img)
                        photo_id = self.data[0]['id']
                        photos += f'photo{self.data[0]["owner_id"]}_{photo_id},'
            elif url_images:
                for url in url_images:
                    url = url.rstrip()
                    if url.split('.')[-1] in IMAGE_EXTENSION:
                        self.upload_image(path_file=path + '/', url=url)
                        photo_id = self.data[0]['id']
                        photos += f'photo{self.data[0]["owner_id"]}_{photo_id},'
                        os.remove(path + '/' + url.split('/')[-1])
            if message == photos == '':
                return False
            params = {
                'message': message,
                'owner_id': '-' + os.getenv('ID_GROUP'),
                'from_group': '1',
                'attachments': photos[:-1]
            }
            self.post.wall.post(**params)
            return True

    def send_post(self, user_id: int, count: int) -> None:
        params = {
            'owner_id': '-' + os.getenv('ID_GROUP'),
            'count': count
        }
        posts = self.post.wall.get(**params)['items'][:count]
        for post in posts:
            self.send_message(user_id, '', f"wall-{os.getenv('ID_GROUP')}_{post['id']}")

    def send_message(self, user_id, message, attachment: str = '') -> None:
        path = r'button.json'
        while True:
            try:
                self.vk.messages.send(user_id=user_id, random_id=random.getrandbits(32), message=message,
                                      attachment=attachment, keyboard=open(path, "r", encoding="UTF-8").read())
                break
            except Exception as e:
                print(e)
                time.sleep(10)

    def commands(self, event) -> None:
        if event.text.lower() == 'помощь' or event.text.lower() == 'help' or event.text.lower() == 'начать':
            self.send_message(user_id=event.user_id, message='Привет, я бот-информатор)')
        elif event.text.lower() == 'меню':
            self.send_message(event.user_id, 'Меню!')
        elif 'запость всё' in event.text.lower() or 'запость все' in event.text.lower():
            with open('../posts/all.json', 'r', encoding='utf-8') as all_file_r:
                all_ = json.load(all_file_r)
                # ХАБР
                habr_all = all_['habr']
                for i in range(habr_all['count'] + 1):
                    if i not in habr_all['post_id']:
                        flag = self.post_post(f'../posts/habr/post_{i}')
                        if flag:
                            self.send_message(event.user_id, 'Пост добавлен!')
                            habr_all['post_id'].append(i)
                        else:
                            self.send_message(event.user_id, f'Не удалось опубликовать пост {i}.')
                #
                with open('../posts/all.json', 'w', encoding='utf-8') as all_file_w:
                    json.dump(all_, all_file_w)
                self.send_message(event.user_id, f"Посты добавлены.")
        elif event.text.lower() == 'покажи последние новости':
            self.send_post(event.user_id, 10)
        elif event.text.lower() == 'парси habr':
            self.habr.parse()
            self.send_message(event.user_id, 'Habr пропарсен.')

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
            print('Auth ERROR:', error_msg)


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