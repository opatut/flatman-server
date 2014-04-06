from flatman import db
from flatman.api import api
from flatman.models import *
# from flatmans.forms import *
from flask import redirect, abort, request, render_template, flash, url_for, g
from datetime import datetime
import json

current_user = User.query.first()

def make_reply(success, data={}):
    data["success"] = True
    return json.dumps(data)

@api.route("/")
def index():
    return make_reply(True, dict(version="0.0.1"))

@api.route("/group/<int:id>")
def group_details(id):
    group = Group.query.filter_by(id=id).first_or_404()
    return make_reply(True, group.toDict())

@api.route("/user")
def current_user_details():
    return make_reply(True, current_user.toDict(private=True))

@api.route("/group/<int:id>/join")
def join_group(id):
    group = Group.query.filter_by(id=id).first_or_404()
    user.group = group
    return make_reply(True)
