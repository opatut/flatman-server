from flatman import app, db
from flatman.models import User, AuthToken

import flask
from flask import request, jsonify, abort, make_response
from flask.ext.restful import Api

api = Api(app, "/api")

# make sure API has Authorization set
@app.before_request
def before_request():
    # only work on API
    if not request.path.startswith("/api/"): return
    print(request.endpoint)
    if request.endpoint in ("api_login", "api_about"): return
    if not get_user(): abort(401)

# @jsonize 
def jsonize(f):
    def wrapper(*args):
        result = f(*args)
        if isinstance(result, tuple):
            result = (jsonify(result[0]), result[1:])
            response = make_response(*result)
        else:
            result = jsonify(result)
            response = make_response(result)

        response.headers.Authorization = "Token"
        return response

    # fix endpoint name
    wrapper.__name__ = f.__name__

    return wrapper 

def get_auth():
    token = request.headers.get("Authorization", "")
    if not token: return None
    auth = AuthToken.query.filter_by(token=token).first()
    return auth

def get_user():
    auth = get_auth()
    if not auth or auth.status != "valid": return None
    return auth.user


import flatman.api.resources

@app.route("/api/about")
@jsonize
def api_about():
    maintenance = False
    return dict(
        message="The server is down for maintenance. We will be back shortly. Thank you for you cooperation!" if maintenance else "Hello World!",  
        version="0.0.2", 
        maintenance=maintenance
    ), 503 if maintenance else 200

@app.route("/api/login")
@jsonize
def api_login():
    # get credentials from Authorization header
    try:
        credentials = flask.json.loads(request.headers.get("Authorization"))
        if not "username" in credentials or not "password" in credentials:
            raise ValueError()
    except (ValueError, TypeError):
        return dict(message="Missing credentials."), 400

    # Find user matching credentials
    user = User.find(credentials["username"])

    if not user or user.password != User.generate_password(credentials["password"]):
        return dict(message="Invalid credentials."), 401

    auth = user.generateAuthToken() 
    return dict(token=auth.toDict(), user=user.toDict())

@app.route("/api/logout")
@jsonize
def api_logout():
    auth = get_auth()
    auth.deleted = True
    db.session.commit()
    return dict(message="Goodbye."), 200

@app.errorhandler(401)
@jsonize
def permission_denied(e):
    return dict(message="Authorization required"), 401
