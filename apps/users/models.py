#!/usr/bin/python
# coding:utf-8


from common.base.base_model import BaseModel
from tortoise import fields


class Users(BaseModel):
    CHOICES = {
        "sex": (
            (1, "男"),
            (2, "女"),
        )
    }
    name = fields.CharField(100, null=False, default="", description="姓名")
    identity = fields.CharField(20, null=False, default="",unique=True, description="证件号")
    sex = fields.SmallIntField(pk=False, default=1, description="性别")
    age = fields.IntField(description="年龄")
    nationlity = fields.CharField(50, null=False, default="", description="国籍")

    class Meta:
        table = "users"