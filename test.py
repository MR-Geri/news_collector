if __name__ == '__main__':
    IMG = ['jpg']
    # url = 'https://file_get/path/name.surname.000.jpg'
    url = 'https://file_get/path/file.jpg'
    url = url.rstrip()
    path = url.split('/')[-1].split('.')
    path = '../' + '_'.join(path[:-1]) + f'.{path[-1]}'
    print(path)
