from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
# from flask.ext.markdown import Markdown
from flask.ext.login import LoginManager
from flask.ext.gravatar import Gravatar
from flask.ext.script import Manager, Server
from flask.ext.assets import Environment, Bundle

app = Flask(__name__)
app.config.from_pyfile("../config.py", silent=True)
manager = Manager(app)
db = SQLAlchemy(app)
# markdown = Markdown(app, safe_mode="escape")
login_manager = LoginManager(app)
gravatar = Gravatar(app, size=48, rating='g', default='identicon', force_default=False, use_ssl=False, base_url=None)
manager.add_command("runserver",  Server(host="0.0.0.0", port=5000))


# setup assets
assets = Environment(app)
assets.debug = True

from webassets.filter import get_filter
scss = get_filter("scss", as_output=True)
scss_all = Bundle("scss/config.scss", "scss/mixins.scss", "scss/main.scss", filters=(scss,), output="gen/scss.css")
css_all = Bundle("css/*.css", scss_all, filters="cssmin", output="gen/main.css")
assets.register("css_all", css_all)

js = Bundle("js/external/*.js", "js/controllers/*.js", "js/*.js", filters='jsmin', output='gen/main.js')
assets.register('js_all', js)

import flatman.models
# import flatman.forms
import flatman.filters
import flatman.views
import flatman.api

login_manager.login_view = "index"

@login_manager.user_loader
def load_user(userid):
    return flatman.models.User.query.filter_by(username=userid).first()
