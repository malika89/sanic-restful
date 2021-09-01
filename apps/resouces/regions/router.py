#!/usr/bin/python
# coding:utf-8


from sanic import Blueprint
from .views import RegionView

router = Blueprint("regions",url_prefix="/regions")
router.add_route(RegionView.as_view(),"/")