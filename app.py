import datetime

from bs4 import BeautifulSoup
from flask import Flask, render_template, url_for, request
from flask_sqlalchemy import SQLAlchemy

from parser_posts.parser import get_html

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.sqlite'
db = SQLAlchemy(app)


def update_class(line: str) -> str:
    if 'class=' in line:
        r_line = line[line.find('class="') + 7:].find('"') + line.find('class="') + 9
        line = line[:line.find('"') - 6] + line[r_line:]
    if '<img' in line:
        line = line.replace('<img ', '<img class="rounded mx-auto d-block mt-3 img-fluid " ')
    return line


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    intro = db.Column(db.String(300), nullable=False)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    flag = db.Column(db.Boolean, default=False)
    url = db.Column(db.Text, default='')

    def __repr__(self):
        return '<Article %r>' % self.id


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/posts', methods=['POST', 'GET'])
def posts():
    page = request.args.get('page', 1, type=int)
    if request.method == 'POST':
        search = request.form['search']
    else:
        search = request.args.get('search', None, type=str)
    if search:
        articles = Article.query.order_by(Article.date.desc()).filter(
            Article.title.like(f'%{search}%') | Article.intro.like(f'%{search}%') | Article.text.like(
                f'%{search}%') |
            Article.id.like(f'%{search}%')
        )
        next_url, prev_url, active, pages = None, None, None, None
    else:
        articles = Article.query.order_by(Article.date.desc()).paginate(page, 5, True)
        next_url = url_for('posts', page=articles.next_num) if articles.has_next else None
        prev_url = url_for('posts', page=articles.prev_num) if articles.has_prev else None
        articles = articles.items
        if page == 1:
            active, pages = 1, [1, 2, 3]
        elif next_url:
            active, pages = page, [page - 1, page, page + 1]
        else:
            active, pages = page, [page - 2, page - 1, page]
    return render_template('posts.html', articles=articles, next_url=next_url, prev_url=prev_url,
                           active=active, pages=pages)


@app.route('/posts/<int:id_>')
def post(id_):
    html = BeautifulSoup(get_html(f'https://habr.com/ru/news/t/{id_}').text, 'html.parser')
    body = str(html.find('div', class_='post__text')).replace('/>', '>').split('\n')
    for i in range(len(body)):
        body[i] = update_class(body[i])
    article = Article.query.get(id_)
    return render_template('test_post_detail.html', article=article).replace('<div></div>', '\n'.join(body))


if __name__ == '__main__':
    app.run()
