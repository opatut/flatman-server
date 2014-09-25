from flatman import db
from flask import json, abort, request, redirect, url_for
from datetime import datetime
from flatman.api import get_user

def has_permission(user, obj, action):
    if hasattr(obj, "has_permission"):
        return obj.has_permission(user, action)

    if hasattr(obj, "permission_parent"):
        return has_permission(user, getattr(obj, obj.permission_parent), action)

    return False


class Api(object):
    def __init__(self, app, urlprefix="/api"):
        self.app = app
        self.urlprefix = urlprefix

    def add_url_rule(self, resource, rule, function, methods):
        print(self.urlprefix + "/" + resource.typename + rule, resource.typename + '_' + function.__name__, function)
        self.app.add_url_rule(self.urlprefix + "/" + resource.typename + rule, resource.typename + '_' + function.__name__, function, methods=methods)

class Filter(object):
    def __init__(self):
        return

    def __call__(self, model_resource, query):
        return query

class PublicFieldFilter(Filter):
    def __init__(self, fields=None, defaults={}):
        self.fields = fields
        self.defaults = defaults or {}

    def __call__(self, model_resource, query):
        request_data = model_resource.get_request_data() or {}

        # get default values, execute functions (lambdas, yay)
        data1 = {field.name: self.defaults[field.name] for field in model_resource.fields if field.name in self.defaults}

        for key, value in data1.iteritems():
            if callable(value):
                data1[key] = value()

        data2 = {field.name: field.convert_set(request_data[field.name]) for field in model_resource.fields if field.name in request_data and field.public}

        data = dict(data1.items() + data2.items())

        for field in model_resource.fields:
            if field.name in data and (self.fields == None or field.name in self.fields):
                query = query.filter_by(**{field.name: data[field.name]})

        return query


class Field(object):
    def __init__(self, name, required=False, public=True):
        self.name = name
        self.required = required
        self.public = public

    def set(self, model, value):
        setattr(model, self.name, self.convert_set(value))

    def get(self, model):
        return self.convert_get(getattr(model, self.name))

    def convert_set(self, value):
        return value

    def convert_get(self, value):
        return value

class DateTimeField(Field):
    def convert_set(self, value):
        return datetime.strptime(value)

    def convert_get(self, value):
        return str(value)

class ModelListField(Field):
    def __init__(self, name, remote_model, remote_id_field="id", required=True, public=True):
        Field.__init__(self, name, required, public)
        self.remote_model = remote_model
        self.remote_id_field = remote_id_field

    def set(self, model, value):
        items = getattr(model, self.name)
        # differences...
        value = [1,2,3,4]

        # remove those that are not included anymore
        items = [item for item in items if getattr(item, self.remote_id_field) in value]

        # add those that are new
        included = [item.id for item in items]
        for id in value:
            if id not in included:
                new_item = self.remote_model.query.filter_by(**{self.remote_id_field: id}).first()
                if new_item:
                    items.append(new_item)
                # else ignore this ID

        # do we need this, a list is a reference?
        setattr(model, self.name, items)

    def convert_get(self, value):
        return [getattr(item, self.remote_id_field) for item in value]


class ModelResource(object):
    def __init__(self, api, model, fields, id_field="id", filters={}, allow_list=True, allow_add=True, allow_update=True, allow_delete=True, allow_get=True, add_defaults={}, typename=None):
        self.api = api
        self.id_field = id_field
        self.model = model
        self.fields = fields
        self.filters = filters 
        if not "default" in self.filters:
            self.filters["default"] = PublicFieldFilter()
        self.allow_list = allow_list
        self.allow_add = allow_add
        self.allow_update = allow_update
        self.allow_delete = allow_delete
        self.allow_get = allow_get
        self.add_defaults = add_defaults
        self.typename = typename or model.__tablename__

        self.expand_fields()
        self.prepare_routes()

    def expand_fields(self):
        self.fields = [Field(field) if isinstance(field, str) else field for field in self.fields]

    def prepare_routes(self):
        if self.allow_list:
            self.api.add_url_rule(self, "", self.list, ("GET",))                        # URL + REST
            self.api.add_url_rule(self, "/<filter>", self.list, ("GET",))               # URL + REST

        if self.allow_add:
            self.api.add_url_rule(self, "/add", self.add, ("POST", "GET"))              # URL
            self.api.add_url_rule(self, "", self.add, ("POST","PUT",))                        # REST

        if self.allow_update:
            self.api.add_url_rule(self, "/<int:id>/update", self.update, ("POST","PUT",))       # URL
            self.api.add_url_rule(self, "/<int:id>", self.update, ("POST","PUT",))      # REST

        if self.allow_delete:
            self.api.add_url_rule(self, "/<int:id>/delete", self.delete, ("DELETE","GET",))     # URL
            self.api.add_url_rule(self, "/<int:id>", self.delete, ("DELETE",))          # REST

        if self.allow_get:
            self.api.add_url_rule(self, "/<int:id>", self.get, ("GET",))                # URL + REST

    def list(self, filter=None):
        # filter = filter or request.args.get("filter", "default")
        filter = filter or "default"
        query = self.model.query
        filtered_query = self.filters[filter](self, query)
        return json.dumps([self.convert_object(item) for item in filtered_query if has_permission(get_user(), item, "get")]), 200

    def get_request_data(self):
        return request.get_json(True, True, True) or None

    def add(self):
        data = self.get_request_data() 

        m = self.model()

        defaults = {k: (v() if callable(v) else v) for k,v in self.add_defaults.iteritems()}
        data = dict(data.items() + defaults.items()) # defaults are overrides for now

        # TODO
        # if not has_permission(get_user(), m, "add"): abort(403)

        for field in self.fields:
            if field.name in data:
                field.set(m, data[field.name])
            elif field.required and field.name != self.id_field:
                print(field.name + " missing")
                return '{}', 400

        db.session.add(m)
        db.session.commit()
        return redirect(url_for("%s_get" % self.typename, id=getattr(m, self.id_field)))

    def update(self, id):
        data = self.get_request_data() 

        m = self.get_object(id)
        if not has_permission(get_user(), m, "update"): abort(403)

        for field in self.fields:
            if field.name in data:
                field.set(m, data[field.name])

        db.session.commit()
        print url_for("%s_get" % self.typename, id=getattr(m, self.id_field))
        return redirect(url_for("%s_get" % self.typename, id=getattr(m, self.id_field)))

    def delete(self, id):
        m = self.get_object(id)
        if not has_permission(get_user(), m, "delete"): abort(403)
        db.session.delete(m)
        db.session.commit()
        return '{}', 200

    def get(self, id):
        obj = self.get_object(id)
        if not obj: abort(404)
        if not has_permission(get_user(), obj, "get"): abort(403)
        return json.dumps(self.convert_object(obj)), 200

    def convert_object(self, obj):
        if not obj: return {}
        return {field.name : field.get(obj) for field in self.fields if field.public}

    def get_object(self, id):
        return self.model.query.filter_by(**{self.id_field:id}).first()
