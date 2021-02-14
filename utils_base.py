import sqlite3
from contextlib import contextmanager


@contextmanager
def get_base(file: str, is_commit: bool = False):
    try:
        con = sqlite3.connect(file)
        sql = con.cursor()
        yield sql
    finally:
        if is_commit:
            con.commit()
        else:
            con.close()


def get_id() -> list:
    with get_base('posts.db') as base:
        return base.execute("""SELECT a.id FROM article a;""").fetchall()
