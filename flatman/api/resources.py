from flatman.api import api, get_user
from flask.ext.restful import Resource
from flatman.models import User
from flask import abort

class GroupResource(Resource):
    def get(self):
        return get_user().group.toDict()

api.add_resource(GroupResource, '/group')

class UserResource(Resource):
    def get(self, id=None):
        current_user = get_user()
        user = User.query.filter_by(id=id).first_or_404() if id else current_user
        if not user in current_user.group.members: abort(403)
        return user.toDict()

api.add_resource(UserResource, '/user/<int:id>', '/user')
