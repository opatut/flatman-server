from flatman import app
from flatman.models import User
from flask import request
from flask.ext.wtf import Form
from wtforms import ValidationError
from wtforms.fields import TextField, SelectField, BooleanField, HiddenField, FieldList, FormField, RadioField, PasswordField, TextAreaField
from wtforms.ext.dateutil.fields import DateTimeField
from wtforms.validators import Required, Length, Regexp, Optional, NoneOf, Email

# Helper class for multiple forms on one page
class MultiForm(Form):
    form_name = HiddenField("form name", validators=[Required()])

    def __init__(self, *args, **kwargs):
        self._form_name = type(self).__name__
        Form.__init__(self, *args, **kwargs)

    def is_submitted(self):
        return Form.is_submitted(self) and request.form.get("form_name") == self._form_name

    def hidden_tag(self, *args, **kwargs):
        self.form_name.data = self._form_name
        return Form.hidden_tag(self, *args, **kwargs)


class Login(object):
    def __init__(self, username_field, message="Username or password are wrong."):
        self.username_field = username_field
        self.message = message

    def __call__(self, form, field):
        password = field.data
        username = form[self.username_field].data
        user = User.find(username)

        if not user or user.password != User.generate_password(password):
            raise ValidationError(self.message)

class RegisterForm(MultiForm):
    username = TextField("Username", validators=[Required()])
    password = PasswordField("Password", validators=[Required()])
    email = TextField("Email", validators=[Required(), Email()])
    displayname = TextField("Display Name", validators=[Optional()])

class LoginForm(MultiForm):
    username = TextField("Username or Email", validators=[Required()])
    password = PasswordField("Password", validators=[Required(), Login("username")])

class ShoppingItemAddForm(MultiForm):
    amount = TextField("Amount", validators=[Optional()])
    title = TextField("Title", validators=[Required()])
    category = TextField("Category", validators=[Optional()])
