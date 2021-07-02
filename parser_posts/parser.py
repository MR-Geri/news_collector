import os
from datetime import datetime, timedelta

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
    def __init__(self, set_flag_post: bool = False, set_flag_post_telegram: bool = False) -> None:
        self.url = 'https://habr.com/ru/news'
        self.dom = 'https://habr.com'
        self.html = get_html(self.url)
        self.set_flag_post = set_flag_post
        self.set_flag_post_telegram = set_flag_post_telegram

    def parse(self) -> None:
        if self.html.status_code == 200:
            pages = 2
            for num in range(1, pages + 1):
                print(f'habr парсинг {num} страницы из {pages}...')
                try:
                    self.create_posts(get_html(f'{self.url}/page{num}/').text)
                except Exception as e:
                    print(e)
        else:
            print(f'{self.html.status_code} ERROR')

    def create_posts(self, html) -> None:
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.find_all('article', class_='post_preview')
        for ind, i in enumerate(items):
            try:
                title = i.find('h2', class_='post__title')
                url = title.find('a').get('href')
                if not is_no_base(url):
                    intro = i.find('div', class_='post__text')
                    post_soup = BeautifulSoup(get_html(url).text, 'html.parser')
                    all_img = []
                    for img in post_soup.find('div', class_='post__text').find_all('img'):
                        if 'https://' in img.get('src'):
                            all_img.append(img.get('src'))
                    # 2021-02-14T13:11Z
                    date = post_soup.find('span', class_='post__time').get('data-time_published').split('T')
                    date = datetime(*map(int, date[0].split('-')), *map(int, date[1][:-1].split(':')))
                    date += timedelta(hours=3)
                    #
                    with get_base(True) as base:
                        base.execute("""
                        INSERT INTO article (id, title, intro, date, flag, url, post_url, teleg_flag)
                        VALUES((SELECT id FROM article ORDER BY id DESC LIMIT 1) + 1, ?, ?, ?, ?, ?, ?, ?)""",
                                     (
                                         title.get_text(strip=True),
                                         intro.get_text(),
                                         date,
                                         self.set_flag_post,
                                         '\n'.join(all_img),
                                         url,
                                         self.set_flag_post_telegram
                                     ))
                    add_users_post_mailing()
                else:
                    break
            except Exception as e:
                print(ind, e)


class ThreeNews:
    def __init__(self, set_flag_post: bool = False, set_flag_post_telegram: bool = False) -> None:
        self.url = 'https://3dnews.ru/news'
        self.html = get_html(self.url)
        self.set_flag_post = set_flag_post
        self.set_flag_post_telegram = set_flag_post_telegram

    def parse(self) -> None:
        if self.html.status_code == 200:
            for i in range(1, 5):
                try:
                    self.create_posts(get_html(f'{self.url}/page-{i}.html').text)
                except Exception as e:
                    print(e)
        else:
            print(f'{self.html.status_code} ERROR')

    def create_posts(self, html) -> None:
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.find_all('div', class_='article-entry')
        for ind, i in enumerate(items):
            try:
                title = i.find('a', class_='entry-header')
                url = self.url + '/'.join(title.get('href').split('/')[:-1])
                if not is_no_base(url):
                    intro = i.find('p')
                    post_soup = BeautifulSoup(get_html(url).text, 'html.parser')
                    # 2021-02-14T14:45:00+03:00
                    date = post_soup.find('span', class_='entry-date').get('content').split('T')
                    date = datetime(*map(int, date[0].split('-')), *map(int, date[1].split(':')[:2]))
                    all_img = []
                    for img in post_soup.find('div', class_='js-mediator-article').find_all('img'):
                        if 'https://' in img.get('src'):
                            all_img.append(img.get('src'))
                    #
                    with get_base(True) as base:
                        base.execute("""
                        INSERT INTO article (id, title, intro, date, flag, url, post_url, teleg_flag)
                        VALUES((SELECT id FROM article ORDER BY id DESC LIMIT 1) + 1, ?, ?, ?, ?, ?, ?, ?)""",
                                     (
                                         title.get_text(strip=True),
                                         intro.get_text(),
                                         date,
                                         self.set_flag_post,
                                         '\n'.join(all_img),
                                         url,
                                         self.set_flag_post_telegram
                                     ))
                    add_users_post_mailing()
            except Exception as e:
                print(ind, e)


if __name__ == '__main__':
    habr = Habr(True, True)
    three_d_news = ThreeNews(True, True)
    habr.parse()
    # three_d_news.parse()
