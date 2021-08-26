#!/usr/bin/python
# coding:utf-8


from common.base.base_model import BaseModel
from tortoise import fields


class Articles(BaseModel):
    name = fields.CharField(100, null=False, default="", description="书名")
    author = fields.CharField(20, null=False, default="", description="作者")
    sn = fields.CharField(100, null=False, default="", description="出版批次")

    class Meta:
        table = "articles"
        unique_together = ["name","author"]