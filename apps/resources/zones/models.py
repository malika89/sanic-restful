#!/usr/bin/python
# coding:utf-8


from common.base.base_model import BaseModel
from tortoise import fields


class Zones(BaseModel):
    CHOICES = {
        "status": (
            (1, "available"),
            (2, "unavailable"),
        )
    }
    name = fields.CharField(100, null=False, default="", description="zone name")
    status = fields.IntField(default=1,choices=CHOICES["status"],description="zone activate status")


    class Meta:
        table = "zones"
