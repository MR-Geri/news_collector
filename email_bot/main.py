import os
import smtplib  # Импортируем библиотеку по работе с SMTP

import requests

from utils_base import get_users, get_post, clear_mailing_posts
from email_bot.bot import *
import time
from email.mime.multipart import MIMEMultipart  # Многокомпонентный объект
from email.mime.text import MIMEText
from email.mime.image import MIMEImage


class SendMessageEmail:
    def __init__(self, email):
        self.server = smtplib.SMTP_SSL('smtp.yandex.com', 465)  # Создаем объект SMTP
        self.server.login(LOGIN, PASSWORD)  # Получаем доступ
        self.message = MIMEMultipart()  # Создаем сообщение
        self.message['From'] = EMAIL  # Адресат
        self.message['To'] = email  # Получатель

    def tls(self):
        self.server.starttls()  # Начинаем шифрованный обмен по TLS

    def topic(self, string):
        self.message['Subject'] = string  # Тема сообщения

    def addText(self, text):
        self.message.attach(MIMEText(text, 'plain'))

    def addImage(self, image, file_name, file_type):
        file = MIMEImage(image.read(), file_type)
        file.add_header('Content-Disposition', 'attachment', filename=file_name)  # Добавляем заголовки
        self.message.attach(file)

    def send(self):
        self.server.send_message(self.message)  # Отправляем сообщение
        self.quit()

    def quit(self):
        self.server.quit()


def check() -> None:
    while True:
        try:
            for user in get_users():
                for post_id in user[2].split():
                    post = get_post(post_id)
                    sending_message_email = SendMessageEmail(user[1])
                    sending_message_email.topic(post[1])
                    for url in post[5].split('\n'):
                        url = url.rstrip()
                        path = '../' + url.split('/')[-1]
                        if url.split('.')[-1] in IMAGE_EXTENSION:
                            with open(path, 'wb') as file:
                                file.write(requests.get(url).content)
                            with open(path, 'rb') as file:
                                sending_message_email.addImage(file, path.split('/')[-1], url.split('.')[-1])
                            os.remove(path)
                    sending_message_email.addText(f'{post[2]}\n\nОригинальная статья: {post[6]}')
                    sending_message_email.send()
                clear_mailing_posts(user[0])
        except Exception as e:
            print(e)
        time.sleep(TIME_UPDATE_MINUTES * 60)


def main():
    check()


if __name__ == '__main__':
    main()
