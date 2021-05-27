import os
import time
import requests
import telebot

from generation_image.main import Post
from telegram_bot.settings import *
from utils_base import get_no_push_posts, set_post_true

bot = telebot.TeleBot(TOKEN)


def push_post() -> None:
    for post in get_no_push_posts('teleg_flag'):
        message = f'{post[1]}\n\n{post[2]}\n\nОригинальная статья: {post[6]}'
        files = []
        paths = []
        set_post_true(post[0], key='teleg_flag')
        if post[6]:
            urls = post[5].split('\n')
            if len(urls) == 1 and len(message) <= 600:
                img_post = Post(int(post[0]))
                img_post.save()
                with open(img_post.path, 'rb') as f:
                    bot.send_media_group('@auto_it_news', [telebot.types.InputMediaPhoto(f)])
                os.remove(img_post.path)
                return
            else:
                for url in urls:
                    url = url.rstrip()
                    path = url.split('/')[-1].split('.')
                    path = '../' + '_'.join(path[:-1]) + f'.{path[-1]}'
                    paths.append(path)
                    if url.split('.')[-1] in IMAGE_EXTENSION:
                        with open(path, 'wb') as file:
                            file.write(requests.get(url).content)
                        files.append(open(path, 'rb'))
            try:
                bot.send_media_group('@auto_it_news', [telebot.types.InputMediaPhoto(f) for f in files])
            except Exception as e:
                print(e)
            bot.send_message('@auto_it_news', f'{message}', parse_mode='markdown', disable_web_page_preview=True)
        for file in files:
            file.close()
        for path in paths:
            os.remove(path)
        time.sleep(1)


def check() -> None:
    while True:
        try:
            push_post()
        except Exception as e:
            print(e)
        time.sleep(TIME_UPDATE_MINUTES * 60)


if __name__ == '__main__':
    check()
