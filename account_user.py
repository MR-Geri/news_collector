from flask import request, render_template, current_app, Blueprint, redirect
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy

from models import Article, Users

blueprint = Blueprint(
    'account_user',
    __name__,
    template_folder='templates'
)
db = SQLAlchemy()
login_manager = LoginManager()


@blueprint.route('/user')
def get_user():
    return 'Тест пройден'


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = Users.query.filter(Users.email == request.form['email']).first()
        if user and user.check_password(request.form['password']):
            login_user(user, remember=request.form.get('check', False))
            return redirect("/")
        return render_template('login.html', message="Неправильный логин или пароль")
    return render_template('login.html')


@blueprint.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        user = Users()
        user.surname = request.form['surname']
        user.name = request.form['name']
        user.email = request.form['email']
        user.set_password(request.form['password'])
        db.session.add(user)
        db.session.commit()
        return redirect('/')
    elif request.method == 'GET':
        return render_template('register.html')


@blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")
