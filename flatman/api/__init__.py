from flask import Flask, Blueprint

api = Blueprint('api', __name__, template_folder='templates')

from flatman.api.views import *
