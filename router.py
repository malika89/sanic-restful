#!/usr/bin/python

import importlib

from common.base.blueprint import BaseBlueprint
from settings import installed_apps

routers = []
for app_ in installed_apps:
    module = importlib.import_module(f"{app_}.router")
    routers.append(getattr(module, "router"))

api = BaseBlueprint.group(routers, url_prefix="/api/v1")
