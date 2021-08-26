#!/usr/bin/python

from common.base.base_view import BaseView
from .models import Articles

class ArticleView(BaseView):
    Model = Articles