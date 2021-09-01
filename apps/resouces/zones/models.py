#!/usr/bin/python
# coding:utf-8


from common.base.base_model import BaseModel
from tortoise import fields


class Zones(BaseModel):
    CHOICES = {
        "status": (
            (1, "可用"),
            (2, "不可用"),
        )
    }
    name = fields.CharField(100, null=False, default="", description="姓名")
    status = fields.IntField(default=1,choices=CHOICES["status"],description="状态")


    class Meta:
        table = "zones"
