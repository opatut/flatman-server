from flatman import app, db
from flask import url_for, session, abort
from datetime import datetime
from random import choice
from hashlib import sha512
from string import printable

class User(db.Model):
    # columns
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    displayname = db.Column(db.String(80))
    email = db.Column(db.String(80))
    password = db.Column(db.String(64))

    # foreign keys
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"))

    # relationships
    auth_tokens = db.relationship("AuthToken", backref="user", lazy="dynamic")

    # login stuff
    def get_id(self):
        return self.username

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    def toDict(self, private=False):
        return dict(id=self.id, 
            username=self.username, 
            displayname=self.displayname,
            email=self.email if private else None,
            group_id=self.group_id)

    def generateAuthToken(self):
        auth = AuthToken(self)
        db.session.add(auth)
        db.session.commit()
        return auth

    @staticmethod
    def generate_password(password):
        return sha512(password).hexdigest()

TOKEN_LENGTH = 128
class AuthToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(255))
    status = db.Column(db.Enum("valid", "revoked", "deleted", name="auth_token_status"), default="valid")
    created = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __init__(self, user):
        self.token = "".join([choice(printable) for x in range(TOKEN_LENGTH)])
        self.status = "valid"
        self.created = datetime.utcnow()
        self.user = user

    def toDict(self):
        return dict(token=self.token, 
            created=str(self.created), 
            user_id=self.user_id)

class Group(db.Model):
    # columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    created = db.Column(db.DateTime)

    # relationships
    members = db.relationship("User", backref="group", lazy="dynamic")
    shopping_categories = db.relationship("ShoppingCategory", backref="group", lazy="dynamic")
    all_shopping_items = db.relationship("ShoppingItem", backref="group", lazy="dynamic")
    all_tasks = db.relationship("Task", backref="group", lazy="dynamic")

    def __init__(self):
        self.created = datetime.utcnow()

    @property
    def tasks(self):
        return self.all_tasks.filter_by(deleted=False)

    @property
    def shopping_items(self):
        return self.all_shopping_items.filter_by(deleted=False)

    def toDict(self):
        return dict(id=self.id, 
            name=self.name, 
            created=str(self.created),
            members=[member.toDict() for member in self.members],
            tasks=[task.toDict() for task in self.tasks],
            shopping_categories=[cat.toDict() for cat in self.shopping_categories],
            shopping_items=[item.toDict() for item in self.shopping_items])

class Task(db.Model):
    # columns
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    description = db.Column(db.Text)
    repeating = db.Column(db.Enum("interval", "ondemand", "single", name="task_repeating"), default="single")
    assignment = db.Column(db.Enum("order", "all", "one", name="task_assignment"), default="one")
    deleted = db.Column(db.Boolean, default=False)
    skippable = db.Column(db.Boolean, default=False) # interval/order
    interval_days = db.Column(db.Integer, default=7)
    interval_start = db.Column(db.DateTime) 
    deadline = db.Column(db.DateTime)

    # foreigh keys
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"))
    assignee_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    # relationships
    assignee = db.relationship("User", backref="assigned_tasks")

    def finish(self):
        if self.repeating == "single":
            db.session.delete(self)
        elif self.repeating == "interval":
            self.interval_start = self.deadline
            self.deadline += timedelta(days=self.interval_days)

        if self.assignment == "order":
            members = list(self.group.members.all())
            if self.assignee in members:
                index = members.index(self.assignee) + 1
                self.assignee = members[index % len(members)]
            else:
                self.assignee = choice(members)

        db.session.commit()


    def toDict(self):
        return dict(id=self.id, 
            title=self.title, 
            description=self.description, 
            repeating=self.repeating,
            assignment=self.assignment,
            interval_days=self.interval_days,
            interval_start=str(self.interval_start) if self.interval_start else None,
            skippable=self.skippable,
            deadline=str(self.deadline) if self.deadline else None,
            assignee_id=self.assignee_id,
            assignee=self.assignee.displayname if self.assignee else None,
            group_id=self.group_id)

class ShoppingItem(db.Model):
    # columns
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    amount = db.Column(db.String(80))
    description = db.Column(db.Text)
    purchased = db.Column(db.Boolean)
    deleted = db.Column(db.Boolean, default=False)

    # foreign keys
    category_id = db.Column(db.Integer, db.ForeignKey("shopping_category.id"))
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"))

    def __init__(self, amount="", title="", category=None):
        self.amount = amount
        self.title = title
        self.category = category
        self.group = category.group if category else None

    def toDict(self):
        return dict(id=self.id, 
            title=self.title, 
            amount=self.amount,
            description=self.description, 
            purchased=self.purchased, 
            category_id=self.category_id,
            group_id=self.group_id)

class ShoppingCategory(db.Model):
    # columns
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))

    # foreign keys
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"))

    # relationships
    all_items = db.relationship("ShoppingItem", backref="category", lazy="dynamic")

    def __init__(self, title="", group=None):
        self.title = title
        self.group = group 

    def toDict(self):
        return dict(id=self.id, 
            title=self.title, 
            group_id=self.group_id)
