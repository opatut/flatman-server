from flatman import app
from flatman.api.views import *
from flatman.forms import RegisterForm, LoginForm
from flatman.models import User

from flask import flash, redirect, url_for, send_from_directory
from flask.ext.login import current_user, login_required, login_user, logout_user

import os.path

@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/login", methods=("POST", "GET"))
def login():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        user = User()
        register_form.populate_obj(user)
        user.password = User.generate_password(User.password)
        login_user(user)
        db.session.add(user)
        db.session.commit()
        flash("Welcome to flatman, %s!" % user.displayname, "success")
        return redirect(request.args.get("next") or url_for("index"))

    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.find(login_form.username.data)
        login_user(user)
        flash("Welcome back, %s!" % user.displayname, "success")
        return redirect(url_for("main"))

    return render_template("login.html", register_form=register_form, login_form=login_form)

@app.route("/logout")
def logout():
    logout_user()
    flash("Bye bye!", "success")
    return redirect(url_for("index"))

@app.route("/templates/<path:filename>")
@login_required
def frontend_templates(filename):
    return send_from_directory(os.path.abspath(os.path.join("flatman", "templates", "frontend")), filename)

@app.route("/")
@login_required
def main():
    return render_template("main.html")
