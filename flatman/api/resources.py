from flatman.api import app, get_user
from flatman.models import User, Task, Group, ShoppingCategory, ShoppingItem, Transaction
from flatman.api.apimachine import ModelResource, Field, DateTimeField, ModelListField, PublicFieldFilter, Api, Filter

api = Api(app, "/api")

ModelResource(api, Task,
    fields=[
        "title", 
        "description", 
        "id", 
        "repeating", 
        "assignment", 
        Field("deleted", public=False), 
        "skippable", 
        "interval_days", 
        "interval_start", 
        "group_id", 
        "assignee_id", 
        DateTimeField("deadline")
    ],
    filters={
        "default": PublicFieldFilter(defaults={"deleted": False, "group_id": lambda: get_user().group_id}),
        "own": PublicFieldFilter(defaults={"deleted": False, "assignee_id": lambda: get_user().id})
    }
)

ModelResource(api, Group,
    fields=[
        "id",
        "name", 
        DateTimeField("created"),
        ModelListField("members", User),
        ModelListField("shopping_categories", ShoppingCategory),
        ModelListField("all_shopping_items", ShoppingItem),
        ModelListField("all_tasks", Task),
        ModelListField("transactions", Transaction)
    ],
    filters={
        "default": Filter(),
        "own": PublicFieldFilter(defaults={"id": lambda: get_user().group_id})
    },
    allow_list=True,
    allow_update=False,
    allow_delete=False,
    allow_add=False)

ModelResource(api, User,
    fields=[
        "id",
        "username",
        "displayname",
        "email",
        "phone",
        "avatar_url",
        DateTimeField("group_joined_date"),
        "group_id",
        "mailhash",
        ModelListField("assigned_tasks", Task)
    ],
    filters={
        "default": Filter(),
        "self": PublicFieldFilter(defaults={"id": lambda: get_user().id})
    },
    allow_delete=False
)

ModelResource(api, ShoppingItem,
    fields=[
        "id",
        Field("title", required=True),
        "amount",
        "description",
        "purchased",
        "category_id",
        Field("group_id", required=True)
    ],
    filters={
        "default": PublicFieldFilter(defaults={"deleted": False, "group_id": lambda: get_user().group_id})
    },
    add_defaults={
        "group_id": lambda: get_user().group_id
    }
)

ModelResource(api, ShoppingCategory,
    fields=[
        "id",
        "title",
        "group_id",
        ModelListField("all_items", ShoppingItem)
    ],
    filters={
        "default": PublicFieldFilter(defaults={"group_id": lambda: get_user().group_id})
    }
)

ModelResource(api, Transaction,
    fields=[
        "id",
        "from_type", 
        "to_type",
        "extern_name",
        "reason",
        "amount",
        DateTimeField("date"),
        "comment",
        "type",
        "group_id",
        "author_id",
        "from_user_id",
        "to_user_id"
    ],
    filters={
        "default": PublicFieldFilter(defaults={"group_id": lambda: get_user().group_id})
    }
)