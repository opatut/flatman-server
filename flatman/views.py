from flatman import app
from flatman.api.views import *
from flatman.forms import RegisterForm, LoginForm, ShoppingItemAddForm
from flatman.models import User, Task, ShoppingCategory, ShoppingItem

from flask import flash, redirect, abort, url_for
from flask.ext.login import current_user, login_required, login_user, logout_user

@app.context_processor
def inject():
    return dict(current_group=current_user.group if current_user.is_authenticated() else None)

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/register", methods=("POST", "GET"))
def register():
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
        return redirect(request.args.get("next") or url_for("index"))

    return render_template("register.html", register_form=register_form, login_form=login_form)

@app.route("/logout")
def logout():
    logout_user()
    flash("Bye bye!", "success")
    return redirect(url_for("index"))

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/members")
@login_required
def members():
    return render_template("members.html")


@app.route("/shopping", methods=("POST", "GET"))
@login_required
def shopping():
    if "clean" in request.args:
        ShoppingItem.query.filter_by(group_id=current_user.group.id, purchased=True).update(dict(deleted=True))
        db.session.commit()
        flash("The list was cleaned.", "success")
        return redirect(url_for("shopping"))

    add_form = ShoppingItemAddForm()

    if add_form.validate_on_submit():
        # see if category exists
        category_string = add_form.category.data.strip()
        category = None
        if category_string:
            category = ShoppingCategory.query.filter(ShoppingCategory.title.like(category_string)).first()
        if not category and category_string:
            category = ShoppingCategory(category_string, current_user.group)
            db.session.add(category)

        item = ShoppingItem(add_form.amount.data.strip(), add_form.title.data.strip(), category)
        item.group = current_user.group
        db.session.add(item)
        db.session.commit()
        flash("The item was added.", "success")
        return redirect(url_for("shopping"))

    return render_template("shopping.html", add_form=add_form)

@app.route("/money")
@login_required
def money():
    return render_template("money.html")

@app.route("/tasks")
@login_required
def tasks():
    return render_template("tasks.html")

@app.route("/tasks/<int:id>")
@login_required
def task(id):
    task = Task.query.filter_by(id=id).first()
    if task.group != current_user.group: abort(403)
    return render_template("tasks.html", task=task)

@app.route("/settings")
@login_required
def settings():
    return render_template("settings.html")
