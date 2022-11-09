#!/usr/bin/python

from common.base.base_view import BaseView

from .models import Region


class RegionView(BaseView):
    Model = Region
