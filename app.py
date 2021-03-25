import account_user
from bs4 import BeautifulSoup
from flask import Flask, render_template, url_for, request
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy

from models import Article
from parser_posts.parser import get_html


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.sqlite'
db = SQLAlchemy(app)  # Важная для работы базы данных строка
from account_user import login_manager

login_manager.init_app(app)
app.register_blueprint(account_user.blueprint)


def update_class(line: str) -> str:
    if 'style=' in line:
        r_line = line[line.find('style="') + 7:].find('"') + line.find('style="') + 8
        line = line[:line.find('"') - 6] + line[r_line:]
    if 'class=' in line:
        r_line = line[line.find('class="') + 7:].find('"') + line.find('class="') + 8
        line = line[:line.find('"') - 6] + line[r_line:]
    if '<img' in line:
        line = line.replace('<img ', '<img class="rounded mx-auto d-block mt-3 img-fluid" ')
    return line


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
            Article.title.like(f'%{search}%') | Article.intro.like(f'%{search}%') | Article.id.like(f'%{search}%')
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
    article = Article.query.get(id_)
    html = BeautifulSoup(get_html(article.post_url).text, 'html.parser')
    if 'habr.com' in article.post_url:
        body = str(html.find('div', class_='post__text')).replace('/>', '>').split('\n')
    else:
        body = str(html.find('div', class_='js-mediator-article')).replace('/>', '>').split('\n')
        if body[-1][-6:] == '</div>':
            body[-1] = body[-1][:-6]
    for i in range(len(body)):
        body[i] = update_class(body[i])
    return render_template('test_post_detail.html', article=article).replace('<div></div>', '\n'.join(body))


if __name__ == '__main__':
    app.run()
