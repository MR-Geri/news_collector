from threading import Thread
import os
import random
import time
from generation_image.main import Post
from utils_base import *
from vk_bot.settings import *
import requests
import vk_api
from vk_api.longpoll import VkEventType
from parser_posts.parser import Habr, ThreeNews
from vk_bot.polls import MyVkLongPoll
from vk_bot.chat_bot import ChatBot


class LocalBot:
    def __init__(self) -> None:
        self.token = TOKEN
        self.vk_session = vk_api.VkApi(token=self.token)
        self.vk = self.vk_session.get_api()
        self.post_session = vk_api.VkApi(app_id=int(APP_ID), scope='wall', token=ACCESS_TOKEN)
        self.post = self.post_session.get_api()
        self.data = None
        self.long = MyVkLongPoll(self.vk_session)
        #
        self.habr = Habr()
        self.three_d_news = ThreeNews(set_flag_post=True)
        #
        self.time_update = time.time()

    def upload_image(self, path_file: str = '', url: str = None) -> None:
        upload_url = self.post.photos.getWallUploadServer(group_id=ID_GROUP)['upload_url']
        if not url:
            photo = open(path_file, 'rb')
        else:
            path = url.split('/')[-1].split('.')
            path = path_file + '_'.join(path[:-1]) + f'.{path[-1]}'
            with open(path, 'wb') as file:
                file.write(requests.get(url).content)
            photo = open(path, 'rb')
        request = requests.post(upload_url, files={'photo': photo})
        params = {'server': request.json()['server'],
                  'photo': request.json()['photo'],
                  'hash': request.json()['hash'],
                  'group_id': ID_GROUP}
        self.data = self.post.photos.saveWallPhoto(**params)

    def send_post(self, user_id: int, count: int) -> None:
        params = {
            'owner_id': '-' + ID_GROUP,
            'count': count
        }
        posts = self.post.wall.get(**params)['items'][:count]
        for post in posts:
            self.send_message(user_id, '', f"wall-{ID_GROUP}_{post['id']}")

    def send_message(self, user_id, message, attachment: str = '') -> None:
        if user_id == MY_ID:
            path = os.path.abspath('my_buttons.json')
        else:
            path = os.path.abspath('button.json')
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
        elif ('запость всё' in event.text.lower() or 'запость все' in event.text.lower()) and event.user_id == MY_ID:
            self.push_post()
        elif event.text.lower() == 'покажи последние новости':
            self.send_post(event.user_id, 10)
        elif event.text.lower() == 'парси' and event.user_id == MY_ID:
            self.parse()
            self.send_message(event.user_id, 'Делаю!')

    def push_post(self) -> None:
        for post in get_no_push_posts():
            try:
                message = f'{post[1]}\n\n{post[2]}\n\nОригинальная статья: {post[6]}'
                photos = ''
                if post[6]:
                    if post[5]:
                        urls = post[5].split('\n')
                        if len(urls) == 1 and len(message) <= 600:
                            img_post = Post(int(post[0]))
                            img_post.save()
                            self.upload_image(img_post.path)
                            photo_id = self.data[0]['id']
                            photos += f'photo{self.data[0]["owner_id"]}_{photo_id},'
                            os.remove(img_post.path)
                            params = {
                                'message': f'{post[6]}',
                                'owner_id': '-' + ID_GROUP,
                                'from_group': '1',
                                'attachments': photos[:-1]
                            }
                        else:
                            for url in urls:
                                url = url.rstrip()
                                if url.split('.')[-1] in IMAGE_EXTENSION:
                                    self.upload_image(path_file='../', url=url)
                                    photo_id = self.data[0]['id']
                                    photos += f'photo{self.data[0]["owner_id"]}_{photo_id},'
                                    os.remove('../' + url.split('/')[-1])
                            params = {
                                'message': message,
                                'owner_id': '-' + ID_GROUP,
                                'from_group': '1',
                                'attachments': photos[:-1]
                            }
                    else:
                        params = {
                            'message': message,
                            'owner_id': '-' + ID_GROUP,
                            'from_group': '1'
                        }
                self.post.wall.post(**params)
                set_post_true(post[0])
                flag = True
            except Exception as e:
                print(e)
                flag = False
            if flag:
                self.send_message(MY_ID, 'Пост добавлен!')
                with get_base() as base:
                    push_chats = base.execute("""SELECT id, chat_id FROM chat_vk WHERE flag = 1;""").fetchall()
                for _, chat_id in push_chats:
                    params = {
                        'owner_id': '-' + ID_GROUP,
                        'count': 1
                    }
                    post = self.post.wall.get(**params)['items'][0]
                    chat_bot.send_message(chat_id, '', f"wall-{ID_GROUP}_{post['id']}")

    def parse(self) -> None:
        self.habr.parse()
        self.three_d_news.parse()

    def start(self) -> None:
        try:
            while True:
                for event in self.long.listen():
                    if event.type == VkEventType.MESSAGE_NEW:
                        if event.from_user and event.to_me and event.text:  # Если написали в ЛС
                            self.commands(event)
        except requests.exceptions.ReadTimeout:
            time.sleep(10)
        except vk_api.AuthError as error_msg:
            print('Auth ERROR:', error_msg)


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
