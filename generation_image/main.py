import os
from typing import Tuple

import requests
from PIL import Image, ImageDraw, ImageFont
from utils_base import get_post


def text_split(len_line: int, text: str) -> list:
    text = text.strip().split()
    out, line = [], ''
    for word in text:
        if len(line) + len(word) <= len_line:
            line += f'{word} '
        else:
            out.append(line)
            line = f'{word} '
    if line:
        out.append(line)
    return out


def get_len_and_size(max_len_line: int, text: str, max_size_line: int) -> Tuple[int, int]:
    text = text.strip()
    size_chr = 1
    len_line = int(max_len_line)
    while (len(text) / len_line) % 1:
        len_line -= 1
    font = ImageFont.truetype('../PT Mono.ttf', size=size_chr)
    size_text = font.getsize('T' * len_line)
    while size_text[0] <= max_size_line:
        size_chr += 1
        font = ImageFont.truetype('../PT Mono.ttf', size=size_chr)
        size_text = font.getsize('T' * len_line)
    return len_line, size_chr - 1


class Post:
    def __init__(self, id_post: int) -> None:
        self.path = ''
        temp = get_post(id_post)
        self.title, self.intro, self.url = temp[1], temp[2], temp[5]
        self.size_image = (936, 1080)
        self.max_size_text = (876, None)
        self.pos = [30, 30]
        self.max_line_text, self.size_chr = 50, 28
        self.im = Image.new('RGB', self.size_image, color=('#2B2B2B'))
        draw_title = text_split(self.max_line_text, self.title)
        draw_intro = text_split(self.max_line_text, self.intro)
        self.font = ImageFont.truetype('../PT Mono.ttf', size=self.size_chr)
        self.ch = self.font.getsize('T')
        self.draw = ImageDraw.Draw(self.im)
        last = self.pos[1] + self.ch[1] * len(draw_title) + len(draw_title) * 0.5 * self.ch[1] + 5
        self.draw.rectangle([(self.pos[0] - 5, self.pos[1] - 5),
                             (self.pos[0] + self.max_size_text[0] + 5, last)],
                            fill="#1B5115")
        self.draw_lines(draw_title, offset=1)
        self.pos[1] += 2 * self.ch[1]
        self.draw_lines(draw_intro, offset=0)
        self.pos[1] += self.ch[1]
        self.add_image()

    def draw_lines(self, lines: list, offset: int) -> None:
        for line in lines:
            size_line = self.font.getsize(line)
            for i in range(-1, offset):
                self.draw.text(
                    (i + self.pos[0] + (self.max_size_text[0] - size_line[0]) / 2, self.pos[1]),
                    line,
                    fill=('white'),
                    font=self.font
                )
            self.pos[1] += self.ch[1] * 1.5

    def add_image(self) -> None:
        url = self.url.rstrip()
        path = f"{url.split('/')[-1]}".split('.')
        self.path = f'../{"".join(path[:-1])}.{path[-1]}'
        with open(self.path, 'wb') as file:
            file.write(requests.get(url).content)
        im = Image.open(self.path)
        size = self.size_image[0], self.size_image[1] - self.pos[1]
        im.thumbnail(size, Image.ANTIALIAS)
        self.im.paste(im, (int((size[0] - im.size[0]) / 2), int(self.pos[1] + (size[1] - im.size[1]) / 2)))
        os.remove(self.path)

    def show(self) -> None:
        self.im.show()

    def save(self) -> None:
        self.im.save(self.path)


def main():
    post = Post(774)
    post.show()


if __name__ == '__main__':
    main()
