import os
import time
import requests
import telebot
from telegram_bot.setting import *
from utils_base import get_no_push_posts, set_post_true

bot = telebot.TeleBot(TOKEN)


def push_post() -> None:
    for post in get_no_push_posts('teleg_flag'):
        message = f'{post[1]}\n\n{post[2]}\n\nОригинальная статья: {post[6]}'
        files = []
        paths = []
        if post[6]:
            for url in post[5].split('\n'):
                url = url.rstrip()
                path = '../' + url.split('/')[-1]
                paths.append(path)
                if url.split('.')[-1] in IMAGE_EXTENSION:
                    with open(path, 'wb') as file:
                        file.write(requests.get(url).content)
                    files.append(open(path, 'rb'))
            bot.send_media_group('@auto_it_news', [telebot.types.InputMediaPhoto(f) for f in files])
            bot.send_message('@auto_it_news', f'{message}', parse_mode='markdown')
        set_post_true(post[0], key='teleg_flag')
        for file in files:
            file.close()
        for path in paths:
            os.remove(path)


def check() -> None:
    while True:
        push_post()
        time.sleep(TIME_UPDATE_MINUTES * 60)


if __name__ == '__main__':
    check()
