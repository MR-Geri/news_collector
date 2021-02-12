import requests

if __name__ == '__main__':
    url = 'https://3dnews.ru/assets/external/illustrations/2021/02/11/1032481/00.jpg'
    with open('temp.jpg', 'wb') as file:
        file.write(requests.get(url).content)
