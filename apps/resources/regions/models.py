#!/usr/bin/python
# coding:utf-8


from common.base.base_model import BaseModel
from tortoise import fields


class Region(BaseModel):
    name = fields.CharField(100, null=False, default="", description=" region name")

    class Meta:
        table = "regions"
        unique_together = ["name"]