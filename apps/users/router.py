#!/usr/bin/python
# coding:utf-8


from common.base.blueprint import BaseBlueprint
from .views import UserViewset


router = BaseBlueprint("users",url_prefix='/user')
router.add_routes(UserViewset.as_view(),'/')