from flatman import app, db, gravatar
from flask import url_for, session, abort, request, Markup
from datetime import datetime
from random import choice
from hashlib import sha512, md5
from string import printable

class User(db.Model):
    # columns
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    displayname = db.Column(db.String(80))
    email = db.Column(db.String(80))
    phone = db.Column(db.String(80))
    password = db.Column(db.String(64))
    avatar_url = db.Column(db.String(180))
    group_joined_date = db.Column(db.DateTime)

    # foreign keys
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"))

    # relationships
    auth_tokens = db.relationship("AuthToken", backref="user", lazy="dynamic")
    transactions_authored = db.relationship("Transaction", backref="author",     lazy="dynamic", foreign_keys="Transaction.author_id")
    transactions_out      = db.relationship("Transaction", backref="from_user",  lazy="dynamic", foreign_keys="Transaction.from_user_id")
    transactions_in       = db.relationship("Transaction", backref="to_user",    lazy="dynamic", foreign_keys="Transaction.to_user_id")

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
            email=self.email,
            mailhash=md5(self.email).hexdigest(),
            phone=self.phone,
            group_id=self.group_id)

    def generateAuthToken(self):
        auth = AuthToken(self)
        db.session.add(auth)
        db.session.commit()
        return auth

    def joinGroup(self, group):
        self.group = group
        self.group_joined_date = datetime.utcnow()

    def get_avatar(self, size=32):
        return gravatar(self.email, size=size)
        #return self.avatar_url or gravatar(self.email, size=size)

    def get_link(self):
        return Markup(u'<a href="{0}">{1}</a>'.format("#", self.displayname))

    @staticmethod
    def generate_password(password):
        return sha512(str(password)).hexdigest()

    @staticmethod
    def find(id):
        id = id.strip()
        return User.query.filter_by(username=id).first() or User.query.filter_by(email=id).first()

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
    transactions = db.relationship("Transaction", backref="group", lazy="dynamic")

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
            shopping_categories={cat.id: cat.toDict() for cat in self.shopping_categories},
            shopping_items=[item.toDict() for item in self.shopping_items],
            transactions=[transaction.toDict() for transaction in self.transactions])

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

    def get_url(self):
        return url_for("task", id=self.id)


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
            item_count=self.all_items.count(),
            group_id=self.group_id)

class Transaction(db.Model):
    # columns
    id = db.Column(db.Integer, primary_key=True)
    from_type = db.Column(db.Enum("user", "extern", "cashbook", name="transaction_from_type"))
    to_type   = db.Column(db.Enum("user", "extern", "cashbook", name="transaction_to_type"))
    extern_name = db.Column(db.String(128))
    reason = db.Column(db.Text)
    amount = db.Column(db.Integer)
    date = db.Column(db.DateTime)
    comment = db.Column(db.Text)
    type = db.Column(db.Enum("normal", "recurring", "reset", name="transaction_type"), default="normal")

    # foreign keys
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"))
    author_id    = db.Column(db.Integer, db.ForeignKey("user.id"))
    from_user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    to_user_id   = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __init__(self, group, author, from_, to_, amount, reason="", extern="", comment="", type="normal"):
        self.group = group
        self.author = author
        self.from_type = "user" if isinstance(from_, User) else from_
        self.from_user = from_  if isinstance(from_, User) else None
        self.to_type   = "user" if isinstance(to_,   User) else to_   
        self.to_user   = to_    if isinstance(to_,   User) else None
        self.amount = amount
        self.reason = reason
        self.extern_name = extern
        self.comment = comment
        self.type = type
        self.date = datetime.utcnow()

    def toDict(self, private=False):
        return dict(id=self.id,
            from_type=self.from_type,
            to_type=self.to_type,
            extern_name=self.extern_name,
            reason=self.reason,
            amount=self.amount,
            date=str(self.date),
            comment=self.comment,
            type=self.type,
            group_id=self.group_id,
            author_id=self.author_id,
            author=self.author.toDict(),
            from_user_id=self.from_user_id,
            from_user=self.from_user.toDict() if self.from_user else None,
            to_user_id=self.to_user_id,
            to_user=self.to_user.toDict() if self.to_user else None
            )
