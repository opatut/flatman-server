from flatman import app
from flatman.api.views import *
from flatman.forms import *

from flask import request
from flatman.models import User

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=("POST", "GET"))
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User()
        form.populate_obj(user)
        user.password = User.generate_password(User.password)
        db.session.add(user)
        db.session.commit()
        flash("Welcome to flatman, %s!" % user.displayname, "success")
        return redirect(url_for("index"))

    return render_template("register.html", form=form)

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

