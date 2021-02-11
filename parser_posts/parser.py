import datetime
import os

import requests
from bs4 import BeautifulSoup
import json

URL = 'https://habr.com/ru/news/'
host = 'https://habr.com/ru/news/'


def get_html(url, params=None):
    try:
        return requests.get(url, params=params)
    except:
        print('ERROR')


def create_post_habr(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('li', class_='content-list__item_post')
    with open('../posts/all.json', encoding='utf-8') as all_:
        all_post = json.load(all_)
        for ind, i in enumerate(items):
            try:
                title = i.find('h2', class_='post__title')
                text = i.find('div', class_='post__text')
                id_ = title.find('a').get('href').split('/')[-2]
                url = title.find('a').get('href')
                img_soup = BeautifulSoup(
                    get_html(url).text, 'html.parser'
                )
                all_img = img_soup.find('div', class_='post__wrapper').find_all('img')
                #
                if id_ not in all_post['habr']['data']:
                    os.mkdir(f"../posts/post_{all_post['habr']['count'] + 1}")
                    with open(
                            f"../posts/post_{all_post['habr']['count'] + 1}/text.txt", 'w', encoding='utf-8'
                    ) as file_text:
                        with open(
                                f"../posts/post_{all_post['habr']['count'] + 1}/image.txt", 'w', encoding='utf-8'
                        ) as file_images:
                            file_text.write(
                                f'{title.get_text(strip=True)}\n\n{text.get_text()}\n\nОригинальная статья: \n{url}'
                            )
                            all_post['habr']['data'].append(id_)
                            for img in all_img:
                                if 'https://' in img.get('src'):
                                    file_images.write(img.get('src') + '\n')
                            all_post['habr']['count'] += 1
            except Exception as e:
                print(ind, e)
    with open('../posts/all.json', 'w', encoding='utf-8') as all_:
        json.dump(all_post, all_)


def get_page_habr(html):
    soup = BeautifulSoup(html, 'html.parser')
    block = soup.find('ul', class_='toggle-menu toggle-menu_pagination')
    return int(block.find_all('li', class_='toggle-menu__item toggle-menu__item_pagination')[-2].get_text())


def parse_habr():
    html = get_html('https://habr.com/ru/news/')
    if html.status_code == 200:
        pages = get_page_habr(html.text)
        for num in range(1, pages + 1):
            print(f'Парсинг {num} страницы из {pages}...')
            create_post_habr(get_html(f'https://habr.com/ru/news/page{num}/').text)
    else:
        print(f'{html.status_code} ERROR')


if __name__ == '__main__':
    date = datetime.datetime.now()
    parse_habr()
    print(datetime.datetime.now() - date)
