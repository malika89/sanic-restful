#!/usr/bin/python


from common.base.blueprint import BaseBlueprint

from .views import ZoneViewset

router = BaseBlueprint("zones", url_prefix="/zones")
router.add_routes(ZoneViewset.as_view(), "/")
