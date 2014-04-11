from flatman import db
from flatman.api import api
from flatman.models import *
# from flatmans.forms import *
from flask import redirect, abort, request, render_template, flash, url_for, g
from datetime import datetime
import json

def get_user(required=True):
    auth = AuthToken.query.filter_by(token=request.form.get("auth")).first()
    if not auth or auth.status != "valid": 
        abort(401)
    return auth.user

def make_reply(success, data={}, error=""):
    data["success"] = success
    if not success:
        data["error_message"] = error
    return json.dumps(data)

def error(msg, **kwargs):
    return make_reply(False, kwargs, error=msg)

@api.route("/")
def index():
    return make_reply(True, dict(version="0.0.1"))

@api.route("/group", methods=("POST",))
def group_details():
    current_user = get_user()
    group = current_user.group
    if not group:
        return error("NO_GROUP")
    return make_reply(True, group.toDict())

@api.route("/user", methods=("POST", ))
def current_user_details():
    current_user = get_user()
    return make_reply(True, current_user.toDict(private=True))

@api.route("/shopping/item/status/<int:id>/<status>", methods=("POST",))
def shopping_item_status(id, status):
    current_user = get_user()
    if not status in ("purchased", "reset"): abort(404)
    item = ShoppingItem.query.filter_by(id=id).first_or_404()
    # if not current_user in item.group.members: abort(403)
    item.purchased = (status == "purchased")
    db.session.commit()
    return make_reply(True)

@api.route("/group/create", methods=("POST",))
def create_group():
    name = request.form.get("name", "").strip()
    errors = {}

    if len(name) < 3:
        errors["name"] = "TOO_SHORT"

    if errors:
        return error("FORM_ERRORS", errors=errors)

    current_user = get_user()
    group = Group()
    group.name = name
    db.session.add(group)
    current_user.group = group
    db.session.commit()
    return make_reply(True)

@api.route("/group/<int:id>/join", methods=("POST",))
def join_group(id):
    current_user = get_user()
    group = Group.query.filter_by(id=id).first_or_404()
    current_user.group = group
    db.session.commit()
    return make_reply(True)

def perform_login(user):
    auth = user.generateAuthToken() 
    return make_reply(True, dict(token=auth.toDict(), user=user.toDict()))

@api.route("/login", methods=("POST", ))
def login():
    f = request.form
    username = f.get("username")
    password = f.get("password")

    user = User.query.filter_by(username=username).first()
    if not user:
        user = User.query.filter_by(email=username).first()
    if not user:
        return error("INVALID_CREDENTIALS", username=username)

    password = User.generate_password(password)
    if user.password != password:
        return error("INVALID_CREDENTIALS")

    return perform_login(user)

@api.route("/register", methods=("POST",))
def register():
    f = request.form
    username = f.get("username")
    email = f.get("email")
    displayname = f.get("displayname")
    password = f.get("password")

    errors = {}

    # validation
    if len(username) < 4:
        errors["username"] = "TOO_SHORT"
    elif User.query.filter_by(username=username).first():
        errors["username"] = "ALREADY_TAKEN"
    elif not re.match(username, "$[a-zA-Z0-9_-]^"):
        errors["username"] = "INVALID"

    if not re.match(email, "$[a-zA-Z0-9_.-]+@[a-zA-Z0-9_.-]+"):
        errors["email"] = "INVALID"

    if len(password) < 6:
        errors["password"] = "TOO_SHORT"
    elif password == username:
        errors["password"] = "INVALID"

    if errors:
        return error("FORM_ERRORS", errors=errors)

    # post-processing

    if not displayname:
        displayname = username
    password = User.generate_password(password)

    user = User()
    user.username = username
    user.displayname = displayname
    user.email = email
    user.password = password
    db.session.add(user)
    db.session.commit()
    return perform_login(user)

@api.errorhandler(401)
def permission_denied(e):
    return error("AUTHORIZATION_REQUIRED"), 401

@api.errorhandler(403)
def permission_denied(e):
    return error("PERMISSION_DENIED"), 403

@api.errorhandler(404)
def permission_denied(e):
    return error("NOT_FOUND"), 404
