from flask import Flask, render_template, session, redirect, url_for, request
from auth import auth, db, Users
from datetime import timedelta

app = Flask(__name__)

app.secret_key = "secret"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(seconds=10)

app.config.update(
    SECRET_KEY="secret",
    SQLALCHEMY_DATABASE_URI='sqlite:///main.db',
    SQLALCHEMY_BINDS={
        'users': 'sqlite:///users.db',
        'info': 'sqlite:///info.db'
    },
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

db.init_app(app)


# Модель info.db
class UserInfo(db.Model):
    __bind_key__ = 'info'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)

    info1 = db.Column(db.Text, default="")
    info2 = db.Column(db.Text, default="")
    info_short = db.Column(db.Text, default="")
    info_full = db.Column(db.Text, default="")
    projects = db.Column(db.Text, default="")


# Главная страница
@app.route("/")
@app.route("/home")
def home():
    users = Users.query.all()
    user_infos = {
        info.username: info
        for info in UserInfo.query.all()
    }

    return render_template(
        "home.html",
        user=None,
        users=users,
        user_infos=user_infos
    )


# Личный кабинет
@app.route("/ls", methods=["GET", "POST"])
def ls():
    username = session.get("username")

    if not username:
        return redirect(url_for("home"))

    user = Users.query.filter_by(username=username).first()

    user_info = UserInfo.query.filter_by(username=username).first()

    if not user_info:
        user_info = UserInfo(username=username)
        db.session.add(user_info)
        db.session.commit()

    if request.method == "POST":

        fields = [
            "info1",
            "info2",
            "info_short",
            "info_full",
            "projects"
        ]

        for field in fields:
            setattr(user_info, field, request.form.get(field, ""))

        db.session.commit()

    return render_template(
        "ls.html",
        user=user,
        user_info=user_info
    )


# Выход
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


app.register_blueprint(auth)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)