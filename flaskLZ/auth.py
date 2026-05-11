import hashlib
from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from logs import log_event

auth = Blueprint('auth', __name__)

db = SQLAlchemy()   # один SQLAlchemy для всего проекта


class Users(db.Model):
    __bind_key__ = 'users'   # таблица в users.db

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


@auth.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = Users.query.filter_by(username=username).first()

        if user:
            salt = username.encode()
            input_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100).hex()

            if user.password == input_hash:
                session['username'] = user.username
                log_event(f"Пользователь {username} вошёл в систему")
                return redirect(url_for('home'))

        return render_template('login.html', error="Неверный логин или пароль")

    return render_template('login.html')


@auth.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        salt = username.encode()
        hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100).hex()

        new_user = Users(username=username, password=hashed_password)

        try:
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect(url_for('home'))
        except:
            db.session.rollback()
            return render_template('register.html', error="Пользователь уже существует")

    return render_template('register.html')


@auth.route("/logout")
def logout():
    username = session.get('username')
    session.clear()
    log_event(f"Пользователь {username} вышел из системы")
    return redirect(url_for('home'))
