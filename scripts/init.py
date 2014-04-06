import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flatman import app, db
from flatman.models import *

db.drop_all()
db.create_all()
db.session.commit()