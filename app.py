import datetime

from flask import Flask, render_template, url_for, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.sqlite'
db = SQLAlchemy(app)


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    intro = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
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
        articles = Article.query.filter(
            Article.title.like(f'%{search}%') | Article.intro.like(f'%{search}%') | Article.text.like(f'%{search}%') |
            Article.id.like(f'%{search}%')
        )
        next_url, prev_url, active, pages = None, None, None, None
    else:
        articles = Article.query.order_by(Article.date.desc()).paginate(page, 5, True)
        next_url = url_for('posts', page=articles.next_num) if articles.has_next else None
        prev_url = url_for('posts', page=articles.prev_num) if articles.has_prev else None
        articles = articles.items
        if page == 1:
            active = 1
            pages = [1, 2, 3]
        elif next_url:
            active = page
            pages = [page - 1, page, page + 1]
        else:
            active = page
            pages = [page - 2, page - 1, page]
    return render_template('posts.html', articles=articles, next_url=next_url, prev_url=prev_url,
                           active=active, pages=pages)


@app.route('/posts/<int:id_>')
def post_detail(id_):
    article = Article.query.get(id_)
    return render_template('post_detail.html', article=article)


if __name__ == '__main__':
    app.run()
