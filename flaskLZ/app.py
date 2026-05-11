from flask import Flask, render_template, session, redirect, url_for, request
from auth import auth, db, Users

app = Flask(__name__)
app.config['SECRET_KEY'] = "secret"

# основная база + бинды
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
app.config['SQLALCHEMY_BINDS'] = {
    'users': 'sqlite:///users.db',
    'info': 'sqlite:///info.db'
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


class UserInfo(db.Model):
    __bind_key__ = 'info'
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
    username = session.get('username')
    if username:
        user = Users.query.filter_by(username=username).first()
        user_info = UserInfo.query.filter_by(username=username).first()
        return render_template('home.html', user=user, user_info=user_info)

    # если не авторизован — список пользователей и их info
    users = Users.query.all()
    infos = UserInfo.query.all()
    return render_template('home.html', user=None, users=users, infos=infos)

@app.route("/admins")
def admins():
    # при заходе на /admins сразу перебрасываем на страницу авторизации
    return redirect(url_for('auth.login'))


@app.route("/private_kabinet", methods=['GET', 'POST'])
def kabinet():
    username = session.get('username')
    if not username:
        return redirect(url_for('auth.login'))

    user_info = UserInfo.query.filter_by(username=username).first()
    if not user_info:
        user_info = UserInfo(username=username)
        db.session.add(user_info)
        db.session.commit()

    if request.method == 'POST':
        user_info.info1 = request.form.get('info1')
        user_info.info2 = request.form.get('info2')
        user_info.info_short = request.form.get('info_short')
        user_info.info_full = request.form.get('info_full')
        user_info.projects = request.form.get('projects')
        db.session.commit()
        return redirect(url_for('kabinet'))

    return render_template('private_kabinet.html', user_info=user_info)


app.register_blueprint(auth)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
