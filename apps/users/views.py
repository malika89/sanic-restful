#!/usr/bin/python
# coding:utf-8

from sanic import response
from common.base.base_view import BaseView,action
from .models import Users


class UserViewset(BaseView):
    Model = Users
    search_fields = ["name"]

    @action(methods=["get","post"],detail=False)
    async def online(self,request,*args,**kwargs):
        return response.json({"code":200,"message":"users online"})