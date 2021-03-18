import os
import smtplib  # Импортируем библиотеку по работе с SMTP

from .bot import *
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
        print('tls')
        self.server.starttls()  # Начинаем шифрованный обмен по TLS

    def topic(self, string):
        self.message['Subject'] = string  # Тема сообщения

    def addText(self, text):
        self.message.attach(MIMEText(text, 'plain'))

    def addImage(self, path, file_type):
        path = os.path.abspath(path)
        file_name = path.split('\\')[-1]
        with open(path, 'rb') as file:
            file = MIMEImage(file.read(), file_type)
            file.add_header('Content-Disposition', 'attachment', filename=file_name)  # Добавляем заголовки
        self.message.attach(file)

    def send(self):
        self.server.send_message(self.message)  # Отправляем сообщение

    def quit(self):
        self.server.quit()


def check() -> None:
    while True:
        try:
            sending_message_email = SendMessageEmail()
            sending_message_email.topic("Скриншот")
            sending_message_email.addImage('screen.png', 'PNG')
            sending_message_email.addText('Сообщение')
            sending_message_email.send()
            sending_message_email.quit()
        except Exception as e:
            print(e)
        time.sleep(TIME_UPDATE_MINUTES * 60)


def main():
    check()
