from flatman import app
from flask.ext.wtf import Form
from wtforms import ValidationError
from wtforms.fields import TextField, SelectField, BooleanField, HiddenField, FieldList, FormField, RadioField, PasswordField, TextAreaField
from wtforms.ext.dateutil.fields import DateTimeField
from wtforms.validators import Required, Length, Regexp, Optional, NoneOf

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

