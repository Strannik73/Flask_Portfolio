from datetime import datetime
import os
import hashlib
from flask import Flask, render_template, session, url_for, request, redirect, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# ОБЯЗАТЕЛЬНО добавь секретный ключ для работы сессий
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "your_super_secret_safe_key")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///first.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Белые списки путей
WHITE_URLS = {"/", "/login", "/register", "/logout", "/home"}

# Модели
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Middleware во Flask делается через before_request
@app.before_request
def check_auth():
    # Пропускаем статику и белые URL
    if request.path.startswith('/static') or request.path in WHITE_URLS:
        return None
    
    # Проверка авторизации
    if 'username' not in session:
        return redirect(url_for('login'))

@app.route("/")
@app.route("/home")
def home():
    username_s = session.get('username')
    user_obj = None
    if username_s:
        user_obj = Users.query.filter_by(username=username_s).first()
    return render_template('home.html', user=user_obj)


@app.route("/register", methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Хеширование с использованием соли (в данном случае username)
        salt = username.encode()
        hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100).hex()
        
        new_user = Users(username=username, password=hashed_password)
        try:
            db.session.add(new_user)
            db.session.commit()
            
            session['username'] = username
            return redirect(url_for('home'))
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")
            return render_template('register.html', error="Пользователь уже существует")
    
    return render_template('register.html')

@app.route("/login", methods=['POST', 'GET'])
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
                return redirect(url_for('home'))
        
        return render_template('login.html', error="Неверный логин или пароль")
        
    return render_template('login.html')

@app.route("/private_kabinet", methods=['GET', 'POST'])
def kabinet():
    username = session.get('username')
    user_obj = Users.query.filter_by(username=username).first()
    
    if request.method == 'POST':
        return redirect(url_for('home'))
    
    # Передаем объект, чтобы работало {{ user.username }}
    return render_template('private_kabinet.html', user=user_obj)


@app.route("/logout")
def logout():
    session.clear() 
    return redirect(url_for('home'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)