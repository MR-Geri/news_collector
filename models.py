import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(250), nullable=False)
    intro = db.Column(db.String(300), nullable=False)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    flag = db.Column(db.Boolean, default=False)
    url = db.Column(db.Text, default='')
    post_url = db.Column(db.Text, default='')
    teleg_flag = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Article %r>' % self.id


class Users(db.Model, UserMixin, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    surname = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)
    password = db.Column(db.Text, nullable=False)
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    image = db.Column(db.Text)
    mailing = db.Column(db.Boolean, nullable=False, default=False)
    mailing_posts = db.Column(db.Text)

    def __repr__(self):
        return '<User %r>' % self.id

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
