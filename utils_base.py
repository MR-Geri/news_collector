import os
import sqlite3
from contextlib import contextmanager


@contextmanager
def get_base(is_commit: bool = False):
    con = sqlite3.connect(os.path.abspath('posts.sqlite'))
    try:
        sql = con.cursor()
        yield sql
    finally:
        if is_commit:
            con.commit()
        else:
            con.close()


def get_id() -> list:
    with get_base() as base:
        return [i[0] for i in base.execute("""SELECT id FROM article;""").fetchall()]


def get_post(id_: int) -> list:
    with get_base() as base:
        return base.execute("""SELECT * FROM article WHERE id = ?;""", (id_, )).fetchall()[0]


def get_no_push_posts() -> list:
    with get_base() as base:
        return base.execute("""SELECT * FROM article WHERE flag = 0;""").fetchall()


def set_post_true(id_: int) -> None:
    with get_base(True) as base:
        base.execute("""UPDATE article SET flag = 1 WHERE id = ?""", (id_, ))
