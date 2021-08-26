#!/usr/bin/python
# coding:utf-8


from sanic import Blueprint
from .views import ArticleView

router = Blueprint("articles",url_prefix="/article")
router.add_route(ArticleView.as_view(),"/")