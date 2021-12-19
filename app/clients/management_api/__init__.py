import inspect

from pydantic import BaseModel

from app.clients.management_api import models
from app.clients.management_api.api_client import (  # noqa F401
    ApiClient,
    AsyncApis,
    SyncApis,
)

for model in inspect.getmembers(models, inspect.isclass):
    if model[1].__module__ == "app.clients.management_api.models":
        model_class = model[1]
        if isinstance(model_class, BaseModel):
            model_class.update_forward_refs()
