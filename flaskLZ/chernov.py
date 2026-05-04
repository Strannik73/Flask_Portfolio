

from datetime import datetime
import os
from flask import Flask, Request, render_template, session, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
import hashlib
from captcha.image import ImageCaptcha
import re


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///first.db'
db = SQLAlchemy(app)

WHITE_URLS = {"/", "/login", "/register", "/logout", "/static"}
DEV_MODE = os.getenv("DEV_MODE", "1") == "1" 

image = ImageCaptcha(width=280, height=90)
data = image.generate('hello17world')
image.write('hello17world','demo.png')

class Users(db.Model):
    id = db.Column(db.Integer,autoincrement=True, primary_key = True)
    username = db.Column(db.String(30), unique=True, nullable = False )
    password = db.Column(db.String(200), nullable = False)
    
    def __repr__(self):
        return f"id:{self.id}. user:{self.username}, password: {self.password}"
    
# with app.app_context():
#     db.create_all()

class Roles(db.Model):
    role_id = db.Column(db.Integer,autoincrement=True, primary_key = True)
    role_name = db.Column(db.String(200), nullable = False)

class Humans(db.Model):
    id = db.Column(db.Integer,autoincrement=True, primary_key = True)
    name = db.Column(db.String(20), nullable = True)
    surname = db.Column(db.String(40), nullable = True)
    login = db.Column(db.String(20), nullable = True)
    email = db.Column(db.String(40),  nullable = True)
    Role = db.Column(db.Integer, db.ForeignKey('roles.role_id'), nullable = True)
    password = db.Column(db.String(100),  nullable = True)
    birthdate = db.Column(db.Date,  nullable = True)

    def __repr__(self):
        return super().__repr__()
    
with app.app_context():
    db.create_all()

@app.middleware('http')
async def session_middleware(request: Request, call_next):
    path = request.url.path
    if path.startswith('/static') or path in WHITE_URLS:
        return await call_next(request)
    
    session_id = request.cookies.get('session_id')
    if not session_id:
        # return RedirectResponse(url='/login')


    session["created"] = datetime.now()
    return await call_next(request)

@app.route("/")
@app.route("/home")
def home():

    username = session.get('username')
    return render_template('home.html', username=username)

@app.route("/register", methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        copy_password = password.encode()
        salt = username.encode()
        hashed_password = str(hashlib.pbkdf2_hmac('sha256', copy_password, salt, 100))
        
        user = Users(username=username, password=hashed_password)
        try:
            db.session.add(user)
            db.session.commit()
            
            session.permanent = True
            session['username'] = username
            
            return redirect(url_for('home'))
        except Exception as e:
            print(e)
            return redirect(url_for('register'))
    
    return render_template('register.html', a='demo.png')

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = Users.query.filter_by(username=username).first()
        
        if user:
            copy_password = password.encode()
            salt = username.encode()
            input_hash = str(hashlib.pbkdf2_hmac('sha256', copy_password, salt, 100))
            
            if user.password == input_hash:
                
                session.permanent = True
                session['username'] = user.username
                return redirect(url_for('home'))
        
        print("Wrong login or password")
        return render_template('login.html', error="Ошибка входа")
        
    return render_template('login.html')

@app.route("/private_kabinet", methods=['POST', 'GET'])
def kabinet():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':

        return redirect('/')
    
  
    return render_template('private_kabinet.html', username=session['username'])

@app.route("/logout")
def logout():
    session.clear() 
    return redirect(url_for('home'))

# if __name__ == "__main__":
#     app.run(debug=True, ssl_context = ('cert.pem', 'key.pem'))

if __name__ == "__main__":
    app.run(debug=True)