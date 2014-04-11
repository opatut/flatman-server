from flatman import app
from flatman.api.views import *

@app.route("/")
def index():
    return render_template("index.html")
