#!/usr/bin/python


from tortoise import fields

from common.base.base_model import BaseModel


class Region(BaseModel):
    name = fields.CharField(
        100, null=False, default="", description=" region name"
    )

    class Meta:
        table = "regions"
        unique_together = ["name"]
