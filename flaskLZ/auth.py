import hashlib
from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from logs import log_event

auth = Blueprint("auth", __name__)

db = SQLAlchemy()


class Users(db.Model):
    __bind_key__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(
        db.String(30),
        unique=True,
        nullable=False
    )
    password = db.Column(
        db.String(200),
        nullable=False
    )


def hash_password(username, password):
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        username.encode(),
        100
    ).hex()


@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = Users.query.filter_by(
            username=username
        ).first()

        if user and user.password == hash_password(username, password):
            session.permanent = True
            session["username"] = username
            log_event(username, "LOGIN", "SUCCESS")
            return redirect(url_for("ls"))

        log_event(username, "LOGIN", "ERROR")

        return render_template(
            "login.html",
            error="Неверный логин или пароль"
        )

    return render_template("login.html")


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        new_user = Users(
            username=username,
            password=hash_password(username, password)
        )
        try:
            db.session.add(new_user)
            db.session.commit()
            session.permanent = True
            session["username"] = username
            log_event(username, "REGISTER", "SUCCESS")
            return redirect(url_for("ls"))
        
        except:
            db.session.rollback()
            log_event(username, "REGISTER", "ERROR")
            return render_template(
                "register.html",
                error="Пользователь уже существует"
            )

    return render_template("register.html")