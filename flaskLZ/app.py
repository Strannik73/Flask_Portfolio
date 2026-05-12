from datetime import timedelta
from flask import Flask, render_template, session, redirect, url_for, request
from auth import auth, db, Users
from logs import init_logs_db, log_event

app = Flask(__name__)

app.secret_key = "secret"

app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(seconds=180)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_BINDS"] = {
    "users": "sqlite:///users.db",
    "info": "sqlite:///info.db"
}

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


class UserInfo(db.Model):
    __bind_key__ = "info"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)

    info1 = db.Column(db.Text, default="")
    info2 = db.Column(db.Text, default="")
    info_short = db.Column(db.Text, default="")
    info_full = db.Column(db.Text, default="")
    projects = db.Column(db.Text, default="")


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


@app.route("/ls", methods=["GET", "POST"])
def ls():
    username = session.get("username")
    if not username:
        return redirect(url_for("auth.login"))
    
    user = Users.query.filter_by(username=username).first()
    user_info = UserInfo.query.filter_by(
        username=username
    ).first()

    if not user_info:
        user_info = UserInfo(username=username)
        db.session.add(user_info)
        db.session.commit()

    if request.method == "POST":
        user_info.info1 = request.form.get("info1", "")
        user_info.info2 = request.form.get("info2", "")
        user_info.info_short = request.form.get("info_short", "")
        user_info.info_full = request.form.get("info_full", "")
        user_info.projects = request.form.get("projects", "")

        db.session.commit()

    return render_template(
        "ls.html",
        user=user,
        user_info=user_info
    )

@app.errorhandler(403)
def handle_403(error):
    username = session.get("username")
    try:
        log_event(username, "ERROR_403", str(error))
    except Exception:
        pass
    return render_template("403.html", user=username, error=str(error)), 403

@app.errorhandler(404)
def handle_404(error):
    username = session.get("username")
    try:
        log_event(username, "ERROR_404", str(error))
    except Exception:
        pass
    return render_template("404.html", user=username, error=str(error)), 404

@app.route("/logout")
def logout():
    username = session.get("username")
    log_event(username, "LOGOUT", "SUCCESS")
    session.clear()
    return redirect(url_for("home"))

app.register_blueprint(auth)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        init_logs_db()
    app.run(host="0.0.0.0", port=5000, ssl_context=('cert.pem', 'key.pem'), debug=False)