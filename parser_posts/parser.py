import os
import time
from datetime import datetime

from utils_base import *
import requests
from bs4 import BeautifulSoup
import json


def get_html(url, params=None):
    try:
        return requests.get(url, params=params)
    except Exception as e:
        print(f'get_html ERROR: {e}')


class Habr:
    def __init__(self) -> None:
        self.url = 'https://habr.com/ru/news/'
        self.html = get_html(self.url)

    def parse(self) -> None:
        if self.html.status_code == 200:
            pages = self.get_page()
            for num in range(1, pages + 1):
                print(f'habr парсинг {num} страницы из {pages}...')
                self.create_posts(get_html(f'{self.url}page{num}/').text)
        else:
            print(f'{self.html.status_code} ERROR')

    def get_page(self) -> int:
        soup = BeautifulSoup(self.html.text, 'html.parser')
        block = soup.find('ul', class_='toggle-menu toggle-menu_pagination')
        return int(block.find_all('li', class_='toggle-menu__item toggle-menu__item_pagination')[-2].get_text())

    @staticmethod
    def create_posts(html) -> None:
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.find_all('li', class_='content-list__item_post')
        with open('../posts/all.json', encoding='utf-8') as all_:
            all_post = json.load(all_)
            for ind, i in enumerate(items):
                try:
                    title = i.find('h2', class_='post__title')
                    id_ = title.find('a').get('href').split('/')[-2]
                    if id_ not in get_id():
                        intro = i.find('div', class_='post__text')
                        url = title.find('a').get('href')
                        post_soup = BeautifulSoup(
                            get_html(url).text, 'html.parser'
                        )
                        all_img = []
                        for img in post_soup.find('div', class_='post__wrapper').find_all('img'):
                            if 'https://' in img.get('src'):
                                all_img.append(img.get('src'))
                        text = post_soup.find('div', class_='post__text').get_text(strip=True)
                        # 2021-02-14T13:11Z
                        date = post_soup.find('span', class_='post__time').get('data-time_published').split('T')
                        date = datetime(*date[0].split('-'), *date[1][:-1].split(':')) + datetime(hour=3)
                        #
                        with get_base('../posts.db', True) as base:
                            _get = """INSERT INTO article (id, title, intro, text, date, flag, url)
                                                VALUES((SELECT id FROM article  ORDER BY id DESC LIMIT 1) + 1,
                                                ?, ?, ?, ?, ?, ?)"""
                            base.execute(_get, (
                                title.get_text(strip=True),
                                intro.get_text(),
                                text,
                                date,
                                True,
                                '\n'.join(all_img)
                            ))
                    else:
                        break
                except Exception as e:
                    print(ind, e)
        with open('../posts/all.json', 'w', encoding='utf-8') as all_:
            json.dump(all_post, all_)


class ThreeNews:
    def __init__(self) -> None:
        self.url = 'https://3dnews.ru/news'
        self.html = get_html(self.url)

    def parse(self) -> None:
        if self.html.status_code == 200:
            for i in range(1, 2):
                self.create_posts(get_html(f'{self.url}/page-{i}.html').text)
        else:
            print(f'{self.html.status_code} ERROR')

    def create_posts(self, html) -> None:
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.find_all('div', class_='article-entry')
        with open('../posts/all.json', encoding='utf-8') as all_:
            all_post = json.load(all_)
            for ind, i in enumerate(items):
                try:
                    id_ = i.find('div', class_='cntPrevWrapper').find('a').get('name')
                    if id_ not in all_post['3dnews']['data']:
                        title = i.find('a', class_='entry-header')
                        intro = i.find('p')
                        url = self.url + '/'.join(title.get('href').split('/')[:-1])
                        post_soup = BeautifulSoup(
                            get_html(url).text, 'html.parser'
                        )
                        text = post_soup.find('div', class_='js-mediator-article').get_text(strip=True)
                        # 2021-02-14T14:45:00+03:00
                        date = post_soup.find('span', class_='entry-date').get('content')
                        all_img = []
                        for img in post_soup.find('div', class_='js-mediator-article').find_all('img'):
                            if 'https://' in img.get('src'):
                                all_img.append(img.get('src'))
                        #
                        with get_base('../posts.db', True) as base:
                            _get = """INSERT INTO article (id, title, intro, text, date, flag, url)
                                                VALUES((SELECT id FROM article  ORDER BY id DESC LIMIT 1) + 1,
                                                ?, ?, ?, ?, ?, ?)"""
                            base.execute(_get, (
                                title.get_text(strip=True),
                                intro.get_text(),
                                text,
                                date,
                                True,
                                '\n'.join(all_img)
                            ))
                        os.mkdir(f"../posts/3dnews/post_{id_}")
                        with open(
                                f"../posts/3dnews/post_{id_}/text.txt",
                                'w', encoding='utf-8'
                        ) as file_text:
                            with open(
                                    f"../posts/3dnews/post_{id_}/image.txt", 'w',
                                    encoding='utf-8'
                            ) as file_images:
                                file_text.write(
                                    f'{title.get_text(strip=True)}\n\n{text.get_text()}\n\nОригинальная статья: \n{url}'
                                )
                                all_post['3dnews']['data'].append([id_, False])
                                for img in all_img:
                                    if 'https://' in img.get('src'):
                                        file_images.write(img.get('src') + '\n')
                except Exception as e:
                    print(ind, e)
        with open('../posts/all.json', 'w', encoding='utf-8') as all_:
            json.dump(all_post, all_)


if __name__ == '__main__':
    habr = Habr()
    three_d_news = ThreeNews()
    habr.parse()
    three_d_news.parse()
