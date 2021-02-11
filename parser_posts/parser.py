import datetime
import requests
from bs4 import BeautifulSoup
from multiprocessing import Process
import json

URL = 'https://habr.com/ru/news/'
host = 'https://habr.com/ru/news/'


def get_html(url, params=None):
    try:
        return requests.get(url, params=params)
    except:
        print('ERROR')


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('li', class_='content-list__item_post')
    data = []
    for i in items:
        try:
            data.append({
                'name': i.find('h2', class_='post__title').get_text(strip=True),
                'url': i.find('h2', class_='post__title').find('a').get('href')
            })
        except:
            pass
    return data


def get_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    block = soup.find('ul', class_='toggle-menu toggle-menu_pagination')
    return int(block.find_all('li', class_='toggle-menu__item toggle-menu__item_pagination')[-2].get_text())


def multiprocess(beginning, end):
    data = []
    for num in range(beginning, end):
        data.extend(get_content(get_html(URL, params={'p': num}).text))
    try:
        d = json.load(open('data.json'))
    except:
        d = []
        print('Была ошибка в считывании информации')
    d.extend(data)
    try:
        with open("data.json", "w") as write_file:
            json.dump(d, write_file)
    except:
        print('Была ошибка в записи информации')


def parse_process(process=5):
    html = get_html(URL)
    if html.status_code == 200:
        pages = get_page(html.text)
        data_process = []
        last = 0
        print(f'Начало {process} парсинга')
        for num in range(1, pages, process):
            data_process.append(Process(target=multiprocess, args=(num, num + process)))
            last = num
        if pages % process != 0:
            data_process.append(Process(target=multiprocess, args=(last, pages + 1)))
        for i in data_process:
            i.start()
        for i in data_process:
            i.join()
        print(f'Конец {process} парсинга')
    else:
        print(f'{html.status_code} ERROR')


def parse():
    html = get_html(URL)
    if html.status_code == 200:
        pages = get_page(html.text)
        data_set = []
        for num in range(1, pages + 1):
            print(f'Парсинг {num} страницы из {pages}...')
            data_set.extend(get_content(get_html(URL, params={'p': num}).text))
        with open('data.json', 'w') as file:
            json.dump(data_set, file)
    else:
        print(f'{html.status_code} ERROR')


if __name__ == '__main__':
    date = datetime.datetime.now()
    parse()
    print(datetime.datetime.now() - date)
